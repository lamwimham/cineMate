"""
CineMate Data Store
SQL DDLs and Async SQLite Interface.
"""

import aiosqlite
import sqlite3
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from cine_mate.core.models import RunStatus

# --- SQL DDL Statements ---

SCHEMA_RUNS = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id TEXT PRIMARY KEY,
    parent_run_id TEXT REFERENCES pipeline_runs(run_id),
    branch_name TEXT DEFAULT 'main',
    commit_msg TEXT,
    status TEXT DEFAULT 'pending',
    dag_snapshot TEXT,
    trace_id TEXT,
    root_hash TEXT,
    created_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_runs_parent ON pipeline_runs(parent_run_id);
CREATE INDEX IF NOT EXISTS idx_runs_trace ON pipeline_runs(trace_id);
"""

SCHEMA_BLOBS = """
-- Content-Addressable Store (The "Objects" Database)
CREATE TABLE IF NOT EXISTS blobs (
    blob_id TEXT PRIMARY KEY,
    relative_path TEXT NOT NULL UNIQUE,
    file_size_bytes INTEGER DEFAULT 0,
    mime_type TEXT,
    ref_count INTEGER DEFAULT 1
);
"""

SCHEMA_NODE_EXECUTIONS = """
CREATE TABLE IF NOT EXISTS node_executions (
    id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    node_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    
    -- Crash Recovery
    external_api_provider TEXT,
    external_job_id TEXT,
    
    -- Errors
    error_msg TEXT,
    error_traceback TEXT,
    
    -- Timing
    started_at DATETIME,
    completed_at DATETIME,
    
    -- Config
    config_snapshot TEXT,
    
    UNIQUE(run_id, node_id)
);

CREATE INDEX IF NOT EXISTS idx_executions_run ON node_executions(run_id);
CREATE INDEX IF NOT EXISTS idx_executions_recovery ON node_executions(external_job_id) 
    WHERE external_job_id IS NOT NULL;
"""

SCHEMA_ARTIFACTS = """
CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    node_id TEXT NOT NULL,
    blob_hash TEXT REFERENCES blobs(blob_id),
    metadata TEXT,
    is_reused BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),
    
    UNIQUE(run_id, node_id)
);

CREATE INDEX IF NOT EXISTS idx_artifacts_run ON artifacts(run_id);
"""

SCHEMA_USERS = """
CREATE TABLE IF NOT EXISTS user_settings (
    user_id TEXT PRIMARY KEY,
    api_mode TEXT DEFAULT 'managed',  -- 'managed' (Credits) or 'byok' (Own Keys)
    byok_config TEXT,                 -- JSON: Metadata/Hashes for BYOK keys
    managed_credits REAL DEFAULT 0.0, -- Local cache of server balance
    last_sync_at DATETIME
);
"""

SCHEMA_TRACES = """
CREATE TABLE IF NOT EXISTS traces (
    trace_id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES pipeline_runs(run_id),
    user_input TEXT,
    agent_response_summary TEXT,
    
    -- Billing
    cost_llm REAL DEFAULT 0.0,
    cost_generation REAL DEFAULT 0.0,
    billing_mode TEXT DEFAULT 'managed',
    route_provider TEXT,              -- Actual upstream provider used
    
    created_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now'))
);
"""


class Store:
    """
    Async SQLite Store for CineMate.
    Implements the Local-First storage pattern.
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize the database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA foreign_keys=ON;")
            
            # Execute schema DDLs one by one
            for schema in [SCHEMA_RUNS, SCHEMA_BLOBS, SCHEMA_NODE_EXECUTIONS, SCHEMA_ARTIFACTS, SCHEMA_TRACES]:
                # Filter out empty statements caused by trailing semicolons
                statements = [s.strip() for s in schema.split(";") if s.strip()]
                for stmt in statements:
                    await db.execute(stmt)
            await db.commit()

    # --- Run Operations ---

    async def create_run(self, run: 'PipelineRun') -> 'PipelineRun':
        """Create a new Pipeline Run (Commit)."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO pipeline_runs 
                (run_id, parent_run_id, branch_name, commit_msg, status, dag_snapshot, trace_id, root_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id, run.parent_run_id, run.branch_name, run.commit_msg,
                    run.status.value, 
                    json.dumps(run.dag_snapshot) if run.dag_snapshot else None,
                    run.trace_id, run.root_hash
                )
            )
            await db.commit()
        return run

    async def update_run_status(self, run_id: str, status: RunStatus):
        """Update the status of an existing run."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE pipeline_runs SET status = ? WHERE run_id = ?",
                (status.value, run_id)
            )
            await db.commit()

    async def get_run(self, run_id: str) -> Optional['PipelineRun']:
        """Get a Pipeline Run by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM pipeline_runs WHERE run_id = ?", (run_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                
                from cine_mate.core.models import PipelineRun, RunStatus
                return PipelineRun(
                    run_id=row["run_id"],
                    parent_run_id=row["parent_run_id"],
                    branch_name=row["branch_name"],
                    commit_msg=row["commit_msg"],
                    status=RunStatus(row["status"]),
                    dag_snapshot=json.loads(row["dag_snapshot"]) if row["dag_snapshot"] else None,
                    trace_id=row["trace_id"],
                    root_hash=row["root_hash"],
                    created_at=datetime.fromisoformat(row["created_at"])
                )
    
    # --- Node Execution Operations ---

    async def upsert_node_execution(self, execution: 'NodeExecution') -> 'NodeExecution':
        """Create or Update a Node Execution record."""
        async with aiosqlite.connect(self.db_path) as db:
            from cine_mate.core.models import NodeConfig
            
            await db.execute(
                """
                INSERT INTO node_executions 
                (id, run_id, node_id, status, retry_count, external_api_provider, external_job_id, error_msg, error_traceback, started_at, completed_at, config_snapshot)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id, node_id) DO UPDATE SET
                    status=excluded.status,
                    retry_count=excluded.retry_count,
                    external_api_provider=excluded.external_api_provider,
                    external_job_id=excluded.external_job_id,
                    error_msg=excluded.error_msg,
                    error_traceback=excluded.error_traceback,
                    started_at=excluded.started_at,
                    completed_at=excluded.completed_at,
                    config_snapshot=excluded.config_snapshot
                """,
                (
                    execution.id, execution.run_id, execution.node_id, 
                    execution.status.value, execution.retry_count,
                    execution.external_api_provider, execution.external_job_id,
                    execution.error_msg, execution.error_traceback,
                    execution.started_at.isoformat() if execution.started_at else None,
                    execution.completed_at.isoformat() if execution.completed_at else None,
                    json.dumps(execution.config_snapshot.model_dump(exclude_unset=True)) if execution.config_snapshot else None
                )
            )
            await db.commit()
        return execution

    async def get_node_execution(self, run_id: str, node_id: str) -> Optional['NodeExecution']:
        """Get a specific Node Execution."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM node_executions WHERE run_id = ? AND node_id = ?", 
                (run_id, node_id)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                
                from cine_mate.core.models import NodeExecution, NodeStatus, NodeConfig
                
                config_data = json.loads(row["config_snapshot"]) if row["config_snapshot"] else None
                config = NodeConfig(**config_data) if config_data else None
                
                return NodeExecution(
                    id=row["id"],
                    run_id=row["run_id"],
                    node_id=row["node_id"],
                    status=NodeStatus(row["status"]),
                    retry_count=row["retry_count"],
                    external_api_provider=row["external_api_provider"],
                    external_job_id=row["external_job_id"],
                    error_msg=row["error_msg"],
                    error_traceback=row["error_traceback"],
                    started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
                    completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
                    config_snapshot=config
                )

    # --- Blob & Artifact Operations ---

    async def register_blob(self, blob: 'BlobMetadata') -> 'BlobMetadata':
        """Register a physical file in the Content-Addressable Store."""
        async with aiosqlite.connect(self.db_path) as db:
            # Upsert if exists (ref_count could be incremented here in a more advanced version)
            await db.execute(
                """
                INSERT OR REPLACE INTO blobs (blob_id, relative_path, file_size_bytes, mime_type)
                VALUES (?, ?, ?, ?)
                """,
                (blob.blob_id, blob.relative_path, blob.file_size_bytes, blob.mime_type)
            )
            await db.commit()
        return blob

    async def get_blob(self, blob_id: str) -> Optional['BlobMetadata']:
        """Get a Blob by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM blobs WHERE blob_id = ?", (blob_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                
                from cine_mate.core.models import BlobMetadata
                return BlobMetadata(
                    blob_id=row["blob_id"],
                    relative_path=row["relative_path"],
                    file_size_bytes=row["file_size_bytes"],
                    mime_type=row["mime_type"]
                )

    async def link_artifact(self, artifact: 'Artifact') -> 'Artifact':
        """Link a Node in a Run to a physical Blob."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO artifacts 
                (id, run_id, node_id, blob_hash, metadata, is_reused)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact.id, artifact.run_id, artifact.node_id, 
                    artifact.blob_hash, json.dumps(artifact.metadata) if artifact.metadata else None,
                    artifact.is_reused
                )
            )
            await db.commit()
        return artifact

    async def get_artifact(self, run_id: str, node_id: str) -> Optional['Artifact']:
        """Get the artifact for a specific node in a run."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM artifacts WHERE run_id = ? AND node_id = ?", 
                (run_id, node_id)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                
                from cine_mate.core.models import Artifact
                metadata = json.loads(row["metadata"]) if row["metadata"] else None
                
                return Artifact(
                    id=row["id"],
                    run_id=row["run_id"],
                    node_id=row["node_id"],
                    blob_hash=row["blob_hash"],
                    metadata=metadata,
                    is_reused=bool(row["is_reused"]),
                    created_at=datetime.fromisoformat(row["created_at"])
                )

    # --- Crash Recovery Helpers ---

    async def find_stuck_executions(self, provider: Optional[str] = None) -> list['NodeExecution']:
        """Find nodes that are EXECUTING or QUEUED with an external job ID."""
        query = """
            SELECT * FROM node_executions 
            WHERE status IN ('executing', 'queued') 
            AND external_job_id IS NOT NULL
        """
        params = []
        if provider:
            query += " AND external_api_provider = ?"
            params.append(provider)
            
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                results = []
                from cine_mate.core.models import NodeExecution, NodeStatus
                for row in rows:
                    results.append(NodeExecution(
                        id=row["id"], run_id=row["run_id"], node_id=row["node_id"],
                        status=NodeStatus(row["status"]),
                        external_job_id=row["external_job_id"],
                        external_api_provider=row["external_api_provider"]
                    ))
                return results


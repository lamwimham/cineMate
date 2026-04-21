"""
CineMate SkillStore — Local File System + SQLite Metadata Store
Supports CRUD operations, YAML frontmatter validation, and auto-generation
provenance tracking (for SkillReviewer).

Storage layout:
    skills/
    ├── skills.db              # SQLite metadata
    ├── data/
    │   ├── style-cyberpunk/
    │   │   └── SKILL.md       # YAML frontmatter + markdown body
    │   └── workflow-short-ad/
    │       └── SKILL.md
"""

import aiosqlite
import hashlib
import yaml
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from cine_mate.skills.models import (
    SkillMetadata, SkillStatus, SkillCategory, SkillFullContent
)


# --- SQL DDL ---

SCHEMA_SKILLS = """
CREATE TABLE IF NOT EXISTS skills (
    name TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    version TEXT DEFAULT '1.0.0',
    author TEXT DEFAULT 'cinemate',
    
    -- Filtering
    agent TEXT,
    scenario TEXT,
    tags TEXT,  -- JSON array
    
    -- Provenance (auto-generation)
    auto_generated INTEGER DEFAULT 0,
    source_run_id TEXT,
    source_error TEXT,
    
    -- Internal
    status TEXT DEFAULT 'enabled',
    content_hash TEXT,
    created_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),
    updated_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
CREATE INDEX IF NOT EXISTS idx_skills_status ON skills(status);
CREATE INDEX IF NOT EXISTS idx_skills_agent ON skills(agent);
CREATE INDEX IF NOT EXISTS idx_skills_scenario ON skills(scenario);
CREATE INDEX IF NOT EXISTS idx_skills_auto_generated ON skills(auto_generated);
"""


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from SKILL.md content.
    Returns (frontmatter_dict, body_string).
    """
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2].strip()
    return fm, body


def _build_frontmatter(meta: SkillMetadata) -> str:
    """Build YAML frontmatter from SkillMetadata."""
    fm = {
        "name": meta.name,
        "description": meta.description,
        "category": meta.category.value,
        "version": meta.version,
        "author": meta.author,
    }
    if meta.agent:
        fm["agent"] = meta.agent
    if meta.scenario:
        fm["scenario"] = meta.scenario
    if meta.tags:
        fm["tags"] = meta.tags
    if meta.auto_generated:
        fm["auto_generated"] = True
    if meta.source_run_id:
        fm["source_run_id"] = meta.source_run_id
    if meta.source_error:
        fm["source_error"] = meta.source_error
    return yaml.dump(fm, default_flow_style=False, allow_unicode=True)


def _compute_hash(content: str) -> str:
    """SHA256 hash of SKILL.md content for change detection."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


class SkillStore:
    """
    Local File System + SQLite Store for CineMate Skills.
    
    Supports:
    - CRUD operations on skills
    - YAML frontmatter validation
    - Auto-generation provenance (for SkillReviewer)
    - Content hash change detection
    """
    
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.data_dir = skills_dir / "data"
        self.db_path = skills_dir / "skills.db"
    
    async def init(self):
        """Initialize database schema and ensure directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA foreign_keys=ON;")
            for stmt in SCHEMA_SKILLS.split(";"):
                stmt = stmt.strip()
                if stmt:
                    await db.execute(stmt)
            await db.commit()
    
    def _skill_dir(self, name: str) -> Path:
        return self.data_dir / name
    
    def _skill_file(self, name: str) -> Path:
        return self._skill_dir(name) / "SKILL.md"
    
    # --- CRUD Operations ---
    
    async def create(self, name: str, content: str, metadata: Optional[SkillMetadata] = None) -> SkillMetadata:
        """
        Create a new skill.
        
        Args:
            name: Unique skill identifier
            content: Full SKILL.md content (with or without frontmatter)
            metadata: Optional metadata override (extracted from frontmatter if not provided)
        
        Returns:
            SkillMetadata for the created skill
        """
        # Parse frontmatter if present
        fm, body = _parse_frontmatter(content)
        
        # Build metadata from frontmatter or override
        if metadata:
            meta = metadata
        else:
            meta = SkillMetadata(
                name=fm.get("name", name),
                description=fm.get("description", ""),
                category=SkillCategory(fm.get("category", "style")),
                version=fm.get("version", "1.0.0"),
                author=fm.get("author", "cinemate"),
                agent=fm.get("agent"),
                scenario=fm.get("scenario"),
                tags=fm.get("tags", []),
                auto_generated=fm.get("auto_generated", False),
                source_run_id=fm.get("source_run_id"),
                source_error=fm.get("source_error"),
            )
        
        # Ensure name matches
        meta.name = name
        
        # Build canonical content (frontmatter + body)
        fm_yaml = _build_frontmatter(meta)
        canonical_content = f"---\n{fm_yaml}---\n\n{body}" if body else f"---\n{fm_yaml}---\n"
        
        # Compute hash
        meta.content_hash = _compute_hash(canonical_content)
        meta.updated_at = datetime.now()
        
        # Write to filesystem
        skill_dir = self._skill_dir(name)
        skill_dir.mkdir(parents=True, exist_ok=True)
        self._skill_file(name).write_text(canonical_content, encoding="utf-8")
        
        # Write to SQLite
        import json
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO skills 
                (name, description, category, version, author, agent, scenario, tags,
                 auto_generated, source_run_id, source_error, status, content_hash, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    meta.name, meta.description, meta.category.value,
                    meta.version, meta.author, meta.agent, meta.scenario,
                    json.dumps(meta.tags),
                    int(meta.auto_generated), meta.source_run_id, meta.source_error,
                    meta.status.value, meta.content_hash,
                    meta.updated_at.isoformat()
                )
            )
            await db.commit()
        
        return meta
    
    async def read(self, name: str) -> Optional[SkillFullContent]:
        """
        Read a skill's full content (progressive disclosure: full load).
        
        Returns:
            SkillFullContent with metadata + body, or None if not found
        """
        # Read from filesystem
        skill_file = self._skill_file(name)
        if not skill_file.exists():
            return None
        
        raw_content = skill_file.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(raw_content)
        
        # Read metadata from SQLite for consistency
        import json
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM skills WHERE name = ?", (name,)) as cursor:
                row = await cursor.fetchone()
        
        if row:
            meta = SkillMetadata(
                name=row["name"],
                description=row["description"],
                category=SkillCategory(row["category"]),
                version=row["version"],
                author=row["author"],
                agent=row["agent"],
                scenario=row["scenario"],
                tags=json.loads(row["tags"]) if row["tags"] else [],
                auto_generated=bool(row["auto_generated"]),
                source_run_id=row["source_run_id"],
                source_error=row["source_error"],
                status=SkillStatus(row["status"]),
                content_hash=row["content_hash"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
        else:
            # Fallback: construct from frontmatter only
            meta = SkillMetadata(
                name=fm.get("name", name),
                description=fm.get("description", ""),
                category=SkillCategory(fm.get("category", "style")),
                version=fm.get("version", "1.0.0"),
                author=fm.get("author", "cinemate"),
                agent=fm.get("agent"),
                scenario=fm.get("scenario"),
                tags=fm.get("tags", []),
                auto_generated=fm.get("auto_generated", False),
                source_run_id=fm.get("source_run_id"),
                source_error=fm.get("source_error"),
                content_hash=_compute_hash(raw_content),
            )
        
        return SkillFullContent(metadata=meta, content=body)
    
    async def update(self, name: str, content: str) -> Optional[SkillMetadata]:
        """
        Update an existing skill's content.
        
        Validates that the skill exists, updates filesystem + SQLite.
        Returns updated metadata or None if skill not found.
        """
        skill_file = self._skill_file(name)
        if not skill_file.exists():
            return None
        
        fm, body = _parse_frontmatter(content)
        
        # Read existing metadata
        existing = await self.read(name)
        if not existing:
            return None
        
        meta = existing.metadata
        
        # Update from new frontmatter if provided
        if "description" in fm:
            meta.description = fm["description"]
        if "category" in fm:
            meta.category = SkillCategory(fm["category"])
        if "version" in fm:
            meta.version = fm["version"]
        if "tags" in fm:
            meta.tags = fm["tags"]
        if "scenario" in fm:
            meta.scenario = fm["scenario"]
        
        # Update hash and timestamp
        canonical_content = f"---\n{_build_frontmatter(meta)}---\n\n{body}" if body else f"---\n{_build_frontmatter(meta)}---\n"
        meta.content_hash = _compute_hash(canonical_content)
        meta.updated_at = datetime.now()
        
        # Write filesystem
        skill_file.write_text(canonical_content, encoding="utf-8")
        
        # Write SQLite
        import json
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE skills SET 
                    description=?, category=?, version=?, tags=?, scenario=?,
                    content_hash=?, updated_at=?
                WHERE name=?
                """,
                (
                    meta.description, meta.category.value, meta.version,
                    json.dumps(meta.tags), meta.scenario,
                    meta.content_hash, meta.updated_at.isoformat(),
                    meta.name
                )
            )
            await db.commit()
        
        return meta
    
    async def delete(self, name: str) -> bool:
        """
        Delete a skill (filesystem + SQLite).
        Returns True if deleted, False if not found.
        """
        skill_file = self._skill_file(name)
        skill_dir = self._skill_dir(name)
        
        if not skill_file.exists():
            return False
        
        # Remove filesystem
        skill_file.unlink()
        if skill_dir.exists() and not any(skill_dir.iterdir()):
            skill_dir.rmdir()
        
        # Remove from SQLite
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM skills WHERE name = ?", (name,))
            await db.commit()
        
        return True
    
    # --- Query Operations ---
    
    async def list_all(self, status: Optional[SkillStatus] = None) -> List[SkillMetadata]:
        """List all skills, optionally filtered by status."""
        import json
        query = "SELECT * FROM skills"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status.value)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
        
        return [
            SkillMetadata(
                name=row["name"],
                description=row["description"],
                category=SkillCategory(row["category"]),
                version=row["version"],
                author=row["author"],
                agent=row["agent"],
                scenario=row["scenario"],
                tags=json.loads(row["tags"]) if row["tags"] else [],
                auto_generated=bool(row["auto_generated"]),
                source_run_id=row["source_run_id"],
                source_error=row["source_error"],
                status=SkillStatus(row["status"]),
                content_hash=row["content_hash"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]
    
    async def exists(self, name: str) -> bool:
        """Check if a skill exists."""
        return self._skill_file(name).exists()

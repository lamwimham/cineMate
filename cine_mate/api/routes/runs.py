"""
CineMate API — Run CRUD Routes
REST API for creating, listing, and querying pipeline runs.
"""

import asyncio
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from cine_mate.core.store import Store
from cine_mate.core.models import PipelineRun, RunStatus
from cine_mate.cli.commands import (
    _mock_intent_parser,
    _build_dag_from_json,
    mock_executor,
)
from cine_mate.engine.orchestrator import Orchestrator
from cine_mate.api.schemas import (
    CreateRunRequest,
    UpdateRunRequest,
    RunResponse,
    RunDetailResponse,
    RunListResponse,
)

router = APIRouter(prefix="/runs", tags=["runs"])


def get_store(db_path: str) -> Store:
    """Get or create Store instance (simplified for MVP)."""
    from pathlib import Path
    store = Store(Path(db_path))
    # Note: init_db should be called once at startup
    return store


@router.get("", response_model=RunListResponse)
async def list_runs(
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    branch: Optional[str] = Query(None, description="Filter by branch"),
    db_path: str = "./cinemate.db",
):
    """List recent pipeline runs with pagination."""
    store = get_store(db_path)
    await store.init_db()

    runs = await store.list_runs(limit=limit, branch=branch)
    result = []
    for run in runs:
        nodes = await store.list_node_executions_for_run(run.run_id)
        result.append(RunResponse.from_core(
            run,
            node_count=len(nodes),
            completed_nodes=sum(1 for n in nodes if n.status.value == "succeeded"),
        ))

    return RunListResponse(runs=result, total=len(result), limit=limit)


@router.get("/{run_id}", response_model=RunDetailResponse)
async def get_run(
    run_id: str,
    db_path: str = "./cinemate.db",
):
    """Get detailed run info with node-level status."""
    store = get_store(db_path)
    await store.init_db()

    run = await store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    nodes = await store.list_node_executions_for_run(run_id)
    return RunDetailResponse.from_core(run, nodes)


@router.post("", response_model=RunResponse, status_code=201)
async def create_run(
    req: CreateRunRequest,
    db_path: str = "./cinemate.db",
):
    """
    Create a new video pipeline run from natural language prompt.
    
    Parses the prompt into a DAG, executes it with the mock provider (MVP),
    and persists the results.
    """
    store = get_store(db_path)
    await store.init_db()

    # Parse intent
    dag_json = _mock_intent_parser(req.prompt, req.style)
    dag = _build_dag_from_json(dag_json)

    # Create run
    run_id = f"run_api_{asyncio.get_event_loop().time():.0f}"
    run = PipelineRun(
        run_id=run_id,
        parent_run_id=req.parent_run_id,
        branch_name=req.branch_name or "main",
        commit_msg=req.prompt,
        status=RunStatus.PENDING,
    )
    await store.create_run(run)

    # Execute pipeline
    orchestrator = Orchestrator(
        store=store,
        run=run,
        dag=dag,
        executor_fn=mock_executor,
    )
    await orchestrator.execute()

    # Return final state
    final_run = await store.get_run(run_id)
    nodes = await store.list_node_executions_for_run(run_id)
    return RunResponse.from_core(
        final_run,
        node_count=len(nodes),
        completed_nodes=sum(1 for n in nodes if n.status.value == "succeeded"),
    )


@router.patch("/{run_id}", response_model=RunResponse)
async def update_run(
    run_id: str,
    req: UpdateRunRequest,
    db_path: str = "./cinemate.db",
):
    """Update run status (e.g., cancel, pause)."""
    store = get_store(db_path)
    await store.init_db()

    run = await store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    await store.update_run_status(run_id, RunStatus(req.status.value))

    final_run = await store.get_run(run_id)
    nodes = await store.list_node_executions_for_run(run_id)
    return RunResponse.from_core(
        final_run,
        node_count=len(nodes),
        completed_nodes=sum(1 for n in nodes if n.status.value == "succeeded"),
    )


@router.delete("/{run_id}", status_code=204)
async def delete_run(
    run_id: str,
    db_path: str = "./cinemate.db",
):
    """Delete a run and all associated data."""
    store = get_store(db_path)
    await store.init_db()

    run = await store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    # Delete via raw SQL (cascade deletes nodes + artifacts)
    import aiosqlite
    async with aiosqlite.connect(store.db_path) as db:
        await db.execute("DELETE FROM pipeline_runs WHERE run_id = ?", (run_id,))
        await db.commit()

    return None

"""
CineMate CLI Commands Implementation
Handles create, loop, and status commands.
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from typing import Optional

import click

from cine_mate.core.store import Store
from cine_mate.core.models import PipelineRun, RunStatus
from cine_mate.engine.dag import PipelineDAG
from cine_mate.engine.orchestrator import Orchestrator
from cine_mate.engine.fsm import NodeState


# =============================================================================
# Mock Executor (MVP default)
# =============================================================================

async def mock_executor(node_id: str, config: dict) -> dict:
    """
    Mock executor that simulates node execution without real API calls.
    Returns deterministic mock results for each node type.
    """
    await asyncio.sleep(0.1)  # Simulate API latency

    mock_outputs = {
        "script_gen": {"output": f"Generated script for: {config.get('prompt', 'unknown')}", "type": "text"},
        "text_to_image": {"output": f"Mock image: {config.get('prompt', 'scene')}", "type": "image"},
        "image_to_video": {"output": "Mock video: 5s clip generated", "type": "video"},
        "text_to_video": {"output": "Mock video: 5s clip from text", "type": "video"},
        "video_compose": {"output": "Mock final video: composed", "type": "video"},
        "tts": {"output": "Mock audio track", "type": "audio"},
        "color_grade": {"output": "Mock color graded", "type": "video"},
    }

    node_type = config.get("type", "unknown")
    result = mock_outputs.get(node_type, {"output": f"Mock output for {node_id}", "type": "unknown"})

    return {
        "status": "success",
        "node_id": node_id,
        "result": result,
        "cost": 0.0,
    }


# =============================================================================
# Create Command
# =============================================================================

async def cmd_create(
    prompt: str,
    style: Optional[str] = None,
    parent_run_id: Optional[str] = None,
    db_path: Optional[str] = None,
    data_dir: Optional[str] = None,
    use_mock: bool = True,
):
    """Execute a video creation pipeline from a natural language prompt."""

    # --- Bootstrap ---
    project_root = Path.cwd()
    actual_db_path = Path(db_path) if db_path else project_root / "cinemate.db"
    actual_data_dir = Path(data_dir) if data_dir else project_root / "cinemate_data"
    actual_data_dir.mkdir(parents=True, exist_ok=True)

    click_echo("=" * 60)
    click_echo("CineMate — AI Video Production OS")
    click_echo("=" * 60)
    click_echo(f"Mode: {'Mock (no API key)' if use_mock else 'Real API'}")
    click_echo(f"DB: {actual_db_path}")
    click_echo(f"Prompt: {prompt}")
    if style:
        click_echo(f"Style: {style}")
    click_echo("")

    # --- Step 1: Initialize Store ---
    click_echo("[1/4] Initializing storage...")
    store = Store(actual_db_path)
    await store.init_db()
    click_echo("  Storage ready.")

    # --- Step 2: Director Agent parses intent ---
    click_echo("[2/4] Director Agent parsing intent...")
    dag_json = await _parse_intent(prompt, style, use_mock)
    click_echo(f"  DAG plan received ({len(dag_json.get('nodes', []))} nodes):")
    for node in dag_json.get("nodes", []):
        parents = node.get("parents", [])
        parent_str = f" <- {', '.join(parents)}" if parents else ""
        click_echo(f"    [{node.get('id')}] {node.get('type')}{parent_str}")
    click_echo("")

    # --- Step 3: Build and execute DAG ---
    click_echo("[3/4] Executing pipeline...")
    dag = _build_dag_from_json(dag_json)
    run_id = f"run_{int(time.time())}"

    run = PipelineRun(
        run_id=run_id,
        parent_run_id=parent_run_id,
        commit_msg=prompt,
        status=RunStatus.PENDING,
    )

    orchestrator = Orchestrator(
        store=store,
        run=run,
        dag=dag,
        executor_fn=mock_executor,
    )

    await orchestrator.execute()

    # Get final run status
    final_run = await store.get_run(run_id)
    completed = len(orchestrator.completed_nodes)
    total = len(dag.graph.nodes())

    click_echo(f"  Run {run_id} completed: {final_run.status.value}")
    click_echo(f"  Nodes executed: {completed}/{total}")
    click_echo("")

    # --- Step 4: Summary ---
    click_echo("[4/4] Pipeline summary:")
    click_echo(f"  Run ID: {run_id}")
    click_echo(f"  Status: {final_run.status.value}")

    # Print artifacts
    for node_id in dag.graph.nodes():
        artifact = await store.get_artifact(run_id, node_id)
        if artifact and artifact.blob_hash:
            click_echo(f"  {node_id} -> {artifact.blob_hash}")
        elif artifact:
            click_echo(f"  {node_id} -> (no artifact)")

    click_echo("")
    click_echo("=" * 60)
    click_echo("Done! Use 'cinemate status' to check system state.")
    click_echo("=" * 60)


# =============================================================================
# Loop Command
# =============================================================================

async def cmd_loop(
    db_path: Optional[str] = None,
    data_dir: Optional[str] = None,
    use_mock: bool = True,
):
    """Interactive conversation mode with the Director Agent."""

    project_root = Path.cwd()
    actual_db_path = Path(db_path) if db_path else project_root / "cinemate.db"
    actual_data_dir = Path(data_dir) if data_dir else project_root / "cinemate_data"
    actual_data_dir.mkdir(parents=True, exist_ok=True)

    click_echo("=" * 60)
    click_echo("CineMate — Interactive Mode")
    click_echo("=" * 60)
    click_echo(f"Mode: {'Mock (no API key)' if use_mock else 'Real API'}")
    click_echo("Type your video description, or 'exit' to quit.")
    click_echo("")

    # Initialize store
    store = Store(actual_db_path)
    await store.init_db()

    while True:
        try:
            user_input = click.prompt("cinemate>", type=str)
        except (KeyboardInterrupt, EOFError):
            click_echo("\nGoodbye!")
            break

        user_input = user_input.strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            click_echo("Goodbye!")
            break
        if user_input.lower() in ("help", "h"):
            click_echo("Commands:")
            click_echo("  <text>  — Create a video from description")
            click_echo("  exit    — Leave interactive mode")
            click_echo("  help    — Show this help")
            continue

        # Process the prompt
        click_echo("")
        click_echo(f"Processing: {user_input}")

        try:
            dag_json = await _parse_intent(user_input, use_mock=use_mock)
            node_count = len(dag_json.get("nodes", []))
            click_echo(f"  Director Agent planned {node_count} nodes:")
            for node in dag_json.get("nodes", []):
                click_echo(f"    - [{node.get('id')}] {node.get('type')}")

            # Execute
            dag = _build_dag_from_json(dag_json)
            run_id = f"run_{int(time.time())}"
            run = PipelineRun(
                run_id=run_id,
                commit_msg=user_input,
                status=RunStatus.PENDING,
            )

            orchestrator = Orchestrator(
                store=store,
                run=run,
                dag=dag,
                executor_fn=mock_executor,
            )
            await orchestrator.execute()
            completed = len(orchestrator.completed_nodes)
            total = len(dag.graph.nodes())
            final_run = await store.get_run(run_id)
            click_echo(f"  Run {run_id}: {final_run.status.value} ({completed}/{total} nodes)")

        except Exception as e:
            click_echo(f"  Error: {e}")

        click_echo("")


# =============================================================================
# Status Command
# =============================================================================

async def cmd_status(
    db_path: Optional[str] = None,
    data_dir: Optional[str] = None,
):
    """Show CineMate system status."""

    project_root = Path.cwd()
    actual_db_path = Path(db_path) if db_path else project_root / "cinemate.db"
    actual_data_dir = Path(data_dir) if data_dir else project_root / "cinemate_data"

    click_echo("=" * 60)
    click_echo("CineMate — System Status")
    click_echo("=" * 60)

    # Database status
    click_echo(f"Database: {actual_db_path}")
    if actual_db_path.exists():
        store = Store(actual_db_path)
        await store.init_db()
        # Count runs
        async with __import__("aiosqlite").connect(actual_db_path) as db:
            db.row_factory = __import__("aiosqlite").Row
            async with db.execute("SELECT COUNT(*) as cnt FROM pipeline_runs") as cursor:
                row = await cursor.fetchone()
                run_count = row["cnt"]
            async with db.execute("SELECT COUNT(*) as cnt FROM blobs") as cursor:
                row = await cursor.fetchone()
                blob_count = row["cnt"]
        click_echo(f"  Runs: {run_count}")
        click_echo(f"  Blobs: {blob_count}")
    else:
        click_echo("  (not initialized yet)")

    # Data directory
    click_echo(f"Data directory: {actual_data_dir}")
    if actual_data_dir.exists():
        click_echo(f"  Exists: yes")
    else:
        click_echo(f"  Exists: no")

    # Skills
    skills_dir = project_root / "cine_mate" / "skills" / "data"
    click_echo(f"Skills directory: {skills_dir}")
    if skills_dir.exists():
        skill_dirs = list(skills_dir.iterdir())
        click_echo(f"  Installed skills: {len(skill_dirs)}")
        for sd in skill_dirs:
            if sd.is_dir():
                click_echo(f"    - {sd.name}")
    else:
        click_echo("  (no skills installed)")

    click_echo("")
    click_echo("=" * 60)


# =============================================================================
# Helpers
# =============================================================================

async def _parse_intent(
    prompt: str,
    style: Optional[str] = None,
    use_mock: bool = True,
) -> dict:
    """
    Parse user intent into a DAG JSON plan.

    For MVP with mock mode, returns a deterministic DAG based on keywords.
    For real mode, would call the DirectorAgent.
    """
    if use_mock:
        return _mock_intent_parser(prompt, style)
    else:
        # Real DirectorAgent integration (requires API key)
        return await _real_intent_parser(prompt, style)


def _mock_intent_parser(prompt: str, style: Optional[str] = None) -> dict:
    """
    Keyword-based mock intent parser for MVP.
    Generates appropriate DAG based on prompt content.
    """
    prompt_lower = prompt.lower()

    # Detect if it looks like a product/ad request
    is_ad = any(kw in prompt_lower for kw in ["ad", "product", "广告", "产品"])
    # Detect if it mentions multiple scenes
    is_multi = any(kw in prompt_lower for kw in ["scene", "场景", "multiple", "多个"])

    if is_ad:
        return {
            "intent": "product_ad",
            "nodes": [
                {"id": "node_hook", "type": "text_to_video", "parents": [], "params": {"prompt": f"Hook: {prompt}"}},
                {"id": "node_demo", "type": "image_to_video", "parents": [], "params": {"prompt": f"Demo: {prompt}"}},
                {"id": "node_cta", "type": "text_to_video", "parents": [], "params": {"prompt": f"CTA: {prompt}"}},
                {"id": "node_compose", "type": "video_compose", "parents": ["node_hook", "node_demo", "node_cta"]},
            ],
        }
    elif is_multi:
        return {
            "intent": "multi_scene",
            "nodes": [
                {"id": "node_script", "type": "script_gen", "parents": [], "params": {"prompt": prompt}},
                {"id": "node_img1", "type": "text_to_image", "parents": ["node_script"], "params": {"prompt": f"Scene 1: {prompt}"}},
                {"id": "node_img2", "type": "text_to_image", "parents": ["node_script"], "params": {"prompt": f"Scene 2: {prompt}"}},
                {"id": "node_vid1", "type": "image_to_video", "parents": ["node_img1"]},
                {"id": "node_vid2", "type": "image_to_video", "parents": ["node_img2"]},
                {"id": "node_compose", "type": "video_compose", "parents": ["node_vid1", "node_vid2"]},
            ],
        }
    else:
        # Default: single scene pipeline
        return {
            "intent": "single_scene",
            "nodes": [
                {"id": "node_script", "type": "script_gen", "parents": [], "params": {"prompt": prompt}},
                {"id": "node_image", "type": "text_to_image", "parents": ["node_script"], "params": {"prompt": prompt}},
                {"id": "node_video", "type": "image_to_video", "parents": ["node_image"]},
            ],
        }


async def _real_intent_parser(prompt: str, style: Optional[str] = None) -> dict:
    """
    Real intent parsing using DirectorAgent.
    Requires DASHSCOPE_API_KEY.
    """
    from cine_mate.agents.director_agent import DirectorAgent
    from cine_mate.agents.tools.engine_tools import EngineTools

    tools = EngineTools(store_path="./cinemate.db")
    await tools.init_db()

    agent = DirectorAgent(
        name="Director",
        use_mock=False,
        engine_tools=tools,
    )

    # Build prompt with optional style
    if style:
        full_prompt = f"Style: {style}\nRequest: {prompt}"
    else:
        full_prompt = prompt

    # Call the agent
    from agentscope.message import Msg
    msg = Msg(name="user", content=full_prompt, role="user")
    response = await agent(msg)

    # Parse response content
    content = response.get_text_content() if hasattr(response, "get_text_content") else str(response.content)

    # Try to extract JSON from response
    try:
        # Look for JSON in the response
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback to mock parser
        print("Warning: Could not parse DirectorAgent response as JSON, using mock parser.")
        return _mock_intent_parser(prompt, style)


def _build_dag_from_json(dag_json: dict) -> PipelineDAG:
    """Build a PipelineDAG from the intent parser JSON output."""
    dag = PipelineDAG()

    for node in dag_json.get("nodes", []):
        node_id = node["id"]
        node_type = node["type"]
        params = node.get("params", {})
        # Include type in params for executor routing
        params["type"] = node_type
        dag.add_node(node_id, node_type, params)

    for node in dag_json.get("nodes", []):
        for parent_id in node.get("parents", []):
            dag.add_edge(parent_id, node["id"])

    return dag


def click_echo(text: str):
    """Wrapper around click.echo for cleaner code."""
    click.echo(text)

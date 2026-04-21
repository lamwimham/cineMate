#!/usr/bin/env python3
"""
Sprint 3 — MVP End-to-End Demo Script

Demonstrates the full CineMate pipeline:
1. Natural Language Input -> Mock Intent Parser -> DAG JSON
2. DAG Construction -> Orchestrator Execution
3. Mock Provider Results with traceable artifacts
4. PipelineRun persistence in SQLite

Usage:
    python scripts/demo_mvp.py                  # Full demo (all 5 chapters)
    python scripts/demo_mvp.py --chapter 3      # Only chapter 3 (orchestrator)
    python scripts/demo_mvp.py --all            # Same as default

Chapters:
    1. Intent Parsing — NL -> DAG JSON
    2. DAG Construction — JSON -> PipelineDAG with edges
    3. Orchestrator Execution — DAG -> Node results via Mock Executor
    4. PipelineRun Lifecycle — Full create + execute + query flow
    5. Multi-Scenario Validation — Single, Ad, Multi-scene prompts
"""

import os
import sys
import json
import asyncio
import time
import argparse
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Color helpers ──────────────────────────────────────────────────────────

class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def log(title, msg, color=Colors.BLUE):
    print(f"\n{color}{Colors.BOLD}{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}{Colors.ENDC}")
    print(f"  {msg}")


def section(title):
    print(f"\n\n{'#' * 60}")
    print(f"# {title}")
    print(f"{'#' * 60}")


def ok(msg):
    print(f"  {Colors.GREEN}[PASS]{Colors.ENDC} {msg}")


def fail(msg):
    print(f"  {Colors.FAIL}[FAIL]{Colors.ENDC} {msg}")


# ── Chapter 1: Intent Parsing ─────────────────────────────────────────────

async def chapter_intent_parsing():
    section("Chapter 1: Intent Parsing — NL -> DAG JSON")

    from cine_mate.cli.commands import _mock_intent_parser

    test_cases = [
        ("赛博朋克城市夜景，霓虹灯闪烁", "single_scene"),
        ("产品广告耳机", "product_ad"),
        ("多个场景的视频", "multi_scene"),
        ("A beautiful sunset over the ocean", "single_scene"),
        ("Product ad for headphones", "product_ad"),
    ]

    passed = 0
    for prompt, expected_intent in test_cases:
        result = _mock_intent_parser(prompt)
        intent = result.get("intent", "")
        node_count = len(result.get("nodes", []))
        if intent == expected_intent:
            ok(f"'{prompt}' -> {intent} ({node_count} nodes)")
            passed += 1
        else:
            fail(f"'{prompt}' -> {intent} (expected {expected_intent})")

    print(f"\n  Result: {passed}/{len(test_cases)} intent parsing tests passed")
    return passed == len(test_cases)


# ── Chapter 2: DAG Construction ───────────────────────────────────────────

async def chapter_dag_construction():
    section("Chapter 2: DAG Construction — JSON -> PipelineDAG")

    from cine_mate.cli.commands import _build_dag_from_json
    from cine_mate.engine.dag import PipelineDAG

    # Test 1: Linear DAG
    log("2.1 Linear DAG (3 nodes)", "script_gen -> text_to_image -> image_to_video")
    dag_json = {
        "intent": "single_scene",
        "nodes": [
            {"id": "node_script", "type": "script_gen", "parents": [], "params": {"prompt": "test"}},
            {"id": "node_image", "type": "text_to_image", "parents": ["node_script"], "params": {"prompt": "test"}},
            {"id": "node_video", "type": "image_to_video", "parents": ["node_image"]},
        ],
    }
    dag = _build_dag_from_json(dag_json)

    assert isinstance(dag, PipelineDAG), "Must return PipelineDAG"
    assert len(dag.graph.nodes()) == 3, f"Expected 3 nodes, got {len(dag.graph.nodes())}"
    assert dag.graph.has_edge("node_script", "node_image"), "Missing edge script->image"
    assert dag.graph.has_edge("node_image", "node_video"), "Missing edge image->video"
    assert dag.node_configs["node_script"]["type"] == "script_gen", "Type not in config"
    ok("Linear DAG: 3 nodes, 2 edges, type in config")

    # Test 2: Branching DAG (ad pipeline)
    log("2.2 Branching DAG (4 nodes)", "hook, demo, CTA -> compose")
    ad_json = {
        "intent": "product_ad",
        "nodes": [
            {"id": "hook", "type": "text_to_video", "parents": [], "params": {"prompt": "hook"}},
            {"id": "demo", "type": "image_to_video", "parents": [], "params": {"prompt": "demo"}},
            {"id": "cta", "type": "text_to_video", "parents": [], "params": {"prompt": "cta"}},
            {"id": "compose", "type": "video_compose", "parents": ["hook", "demo", "cta"]},
        ],
    }
    dag = _build_dag_from_json(ad_json)

    assert len(dag.graph.nodes()) == 4, f"Expected 4 nodes, got {len(dag.graph.nodes())}"
    assert dag.graph.has_edge("hook", "compose"), "Missing edge hook->compose"
    assert dag.graph.has_edge("demo", "compose"), "Missing edge demo->compose"
    assert dag.graph.has_edge("cta", "compose"), "Missing edge cta->compose"
    ok("Branching DAG: 4 nodes, 3 edges, convergence at compose")

    # Test 3: Multi-scene DAG (6 nodes)
    log("2.3 Multi-scene DAG (6 nodes)", "script -> img1, img2 -> vid1, vid2 -> compose")
    multi_json = {
        "intent": "multi_scene",
        "nodes": [
            {"id": "script", "type": "script_gen", "parents": []},
            {"id": "img1", "type": "text_to_image", "parents": ["script"]},
            {"id": "img2", "type": "text_to_image", "parents": ["script"]},
            {"id": "vid1", "type": "image_to_video", "parents": ["img1"]},
            {"id": "vid2", "type": "image_to_video", "parents": ["img2"]},
            {"id": "compose", "type": "video_compose", "parents": ["vid1", "vid2"]},
        ],
    }
    dag = _build_dag_from_json(multi_json)

    assert len(dag.graph.nodes()) == 6
    assert dag.graph.has_edge("img1", "vid1")
    assert dag.graph.has_edge("img2", "vid2")
    assert dag.graph.has_edge("vid1", "compose")
    assert dag.graph.has_edge("vid2", "compose")
    ok("Multi-scene DAG: 6 nodes, correct parallel + convergence structure")

    print(f"\n  Result: 3/3 DAG construction tests passed")
    return True


# ── Chapter 3: Orchestrator Execution ─────────────────────────────────────

async def chapter_orchestrator_execution():
    section("Chapter 3: Orchestrator Execution — DAG -> Results")

    from cine_mate.cli.commands import _build_dag_from_json, _mock_intent_parser, mock_executor
    from cine_mate.core.store import Store
    from cine_mate.core.models import PipelineRun, RunStatus
    from cine_mate.engine.orchestrator import Orchestrator

    # Setup
    db_path = Path(tempfile.mktemp(suffix=".db"))
    store = Store(db_path)
    await store.init_db()

    # Create DAG from NL prompt
    prompt = "赛博朋克城市夜景"
    dag_json = _mock_intent_parser(prompt)
    dag = _build_dag_from_json(dag_json)

    log("3.1 Pipeline execution", f"Prompt: '{prompt}' ({len(dag_json['nodes'])} nodes)")

    run = PipelineRun(
        run_id="demo_run_001",
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

    # Verify results
    final_run = await store.get_run("demo_run_001")
    assert final_run is not None, "Run not persisted"
    assert final_run.status == RunStatus.COMPLETED, f"Expected COMPLETED, got {final_run.status}"
    ok(f"Run {final_run.run_id} completed: {final_run.status.value}")

    # Verify all nodes executed
    completed = len(orchestrator.completed_nodes)
    total = len(dag.graph.nodes())
    assert completed == total, f"Expected {total} completed, got {completed}"
    ok(f"All nodes executed: {completed}/{total}")

    # Verify node execution records in DB
    for node_id in dag.graph.nodes():
        exec_record = await store.get_node_execution("demo_run_001", node_id)
        assert exec_record is not None, f"No execution record for {node_id}"
        assert exec_record.status.value == "succeeded", f"{node_id} not succeeded"
    ok("All node execution records persisted in SQLite")

    print(f"\n  Result: Orchestrator execution completed successfully")
    return True


# ── Chapter 4: PipelineRun Lifecycle ──────────────────────────────────────

async def chapter_pipeline_run_lifecycle():
    section("Chapter 4: PipelineRun Lifecycle — Full flow")

    from cine_mate.cli.commands import _build_dag_from_json, _mock_intent_parser, mock_executor
    from cine_mate.core.store import Store
    from cine_mate.core.models import PipelineRun, RunStatus
    from cine_mate.engine.orchestrator import Orchestrator

    db_path = Path(tempfile.mktemp(suffix=".db"))
    store = Store(db_path)
    await store.init_db()

    log("4.1 Create run", "PipelineRun with metadata")
    run = PipelineRun(
        run_id="lifecycle_demo",
        parent_run_id=None,
        branch_name="main",
        commit_msg="Demo lifecycle test",
        status=RunStatus.PENDING,
    )
    await store.create_run(run)
    saved_run = await store.get_run("lifecycle_demo")
    assert saved_run is not None
    assert saved_run.commit_msg == "Demo lifecycle test"
    ok("PipelineRun created and retrieved")

    log("4.2 Execute pipeline", "Full DAG execution with status updates")
    dag_json = _mock_intent_parser("产品广告耳机")
    dag = _build_dag_from_json(dag_json)

    orchestrator = Orchestrator(
        store=store,
        run=saved_run,
        dag=dag,
        executor_fn=mock_executor,
    )
    await orchestrator.execute()

    # Verify final state
    final = await store.get_run("lifecycle_demo")
    assert final.status == RunStatus.COMPLETED
    ok(f"Final status: {final.status.value}")

    log("4.3 Query run history", "Multiple runs in database")
    # Create another run
    run2 = PipelineRun(
        run_id="lifecycle_demo_2",
        commit_msg="Second run",
        status=RunStatus.PENDING,
    )
    await store.create_run(run2)

    # Query via raw SQL (placeholder for future store.list_runs())
    async with __import__("aiosqlite").connect(db_path) as db:
        db.row_factory = __import__("aiosqlite").Row
        async with db.execute("SELECT COUNT(*) as cnt FROM pipeline_runs") as cursor:
            count = (await cursor.fetchone())["cnt"]
    assert count == 2, f"Expected 2 runs, got {count}"
    ok(f"Database contains {count} runs")

    print(f"\n  Result: PipelineRun lifecycle verified")
    return True


# ── Chapter 5: Multi-Scenario Validation ──────────────────────────────────

async def chapter_multi_scenario():
    section("Chapter 5: Multi-Scenario Validation — 3 DAG types")

    from cine_mate.cli.commands import _build_dag_from_json, _mock_intent_parser, mock_executor
    from cine_mate.core.store import Store
    from cine_mate.core.models import PipelineRun, RunStatus
    from cine_mate.engine.orchestrator import Orchestrator

    scenarios = [
        ("赛博朋克城市夜景", "single_scene", 3),
        ("产品广告耳机", "product_ad", 4),
        ("多个场景的视频", "multi_scene", 6),
    ]

    db_path = Path(tempfile.mktemp(suffix=".db"))
    store = Store(db_path)
    await store.init_db()

    passed = 0
    for i, (prompt, expected_type, expected_nodes) in enumerate(scenarios):
        log(f"5.{i+1} Scenario: {expected_type}", f"'{prompt}' -> {expected_nodes} nodes")

        dag_json = _mock_intent_parser(prompt)
        assert dag_json["intent"] == expected_type, f"Wrong intent: {dag_json['intent']}"
        assert len(dag_json["nodes"]) == expected_nodes, f"Wrong node count: {len(dag_json['nodes'])}"

        dag = _build_dag_from_json(dag_json)
        run = PipelineRun(
            run_id=f"scenario_{expected_type}",
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

        final = await store.get_run(f"scenario_{expected_type}")
        assert final.status == RunStatus.COMPLETED
        ok(f"Intent: {expected_type}, Nodes: {expected_nodes}, Status: completed")
        passed += 1

    print(f"\n  Result: {passed}/{len(scenarios)} scenarios passed")
    return passed == len(scenarios)


# ── Main Runner ───────────────────────────────────────────────────────────

async def run_all():
    """Run all demo chapters and report results."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║     CineMate — MVP End-to-End Demo (Sprint 3)           ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    chapters = {
        1: ("Intent Parsing", chapter_intent_parsing),
        2: ("DAG Construction", chapter_dag_construction),
        3: ("Orchestrator Execution", chapter_orchestrator_execution),
        4: ("PipelineRun Lifecycle", chapter_pipeline_run_lifecycle),
        5: ("Multi-Scenario Validation", chapter_multi_scenario),
    }

    results = {}
    for num, (name, fn) in chapters.items():
        try:
            results[num] = await fn()
        except Exception as e:
            print(f"\n  {Colors.FAIL}[ERROR]{Colors.ENDC} Chapter {num} failed: {e}")
            import traceback
            traceback.print_exc()
            results[num] = False

    # Summary
    print(f"\n\n{Colors.BOLD}{Colors.CYAN}")
    print(f"  {'=' * 60}")
    print(f"  DEMO SUMMARY")
    print(f"  {'=' * 60}{Colors.ENDC}")

    for num, (name, _) in chapters.items():
        status = f"{Colors.GREEN}PASS{Colors.ENDC}" if results[num] else f"{Colors.FAIL}FAIL{Colors.ENDC}"
        print(f"  Chapter {num}: {name:35s} {status}")

    total = sum(1 for v in results.values() if v)
    print(f"\n  Total: {total}/{len(chapters)} chapters passed")

    if total == len(chapters):
        print(f"\n  {Colors.GREEN}{Colors.BOLD}All chapters passed! MVP demo successful.{Colors.ENDC}\n")
    else:
        print(f"\n  {Colors.FAIL}{Colors.BOLD}Some chapters failed. Check errors above.{Colors.ENDC}\n")

    return total == len(chapters)


def main():
    parser = argparse.ArgumentParser(description="CineMate MVP End-to-End Demo")
    parser.add_argument("--chapter", type=int, choices=[1, 2, 3, 4, 5],
                        help="Run a specific chapter only")
    parser.add_argument("--all", action="store_true", help="Run all chapters (default)")
    args = parser.parse_args()

    chapters = {
        1: ("Intent Parsing", chapter_intent_parsing),
        2: ("DAG Construction", chapter_dag_construction),
        3: ("Orchestrator Execution", chapter_orchestrator_execution),
        4: ("PipelineRun Lifecycle", chapter_pipeline_run_lifecycle),
        5: ("Multi-Scenario Validation", chapter_multi_scenario),
    }

    if args.chapter:
        name, fn = chapters[args.chapter]
        print(f"\nRunning Chapter {args.chapter}: {name}\n")
        result = asyncio.run(fn())
        sys.exit(0 if result else 1)
    else:
        result = asyncio.run(run_all())
        sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()

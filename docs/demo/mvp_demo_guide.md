# MVP End-to-End Demo Guide (Sprint 3)

## Overview

This demo validates the complete CineMate MVP pipeline from natural language input to video pipeline execution using Mock providers. No API keys required.

## Demo Flow

```
Natural Language
       ↓
[Chapter 1] Intent Parser → DAG JSON (single/ad/multi-scene)
       ↓
[Chapter 2] DAG Construction → PipelineDAG with edges
       ↓
[Chapter 3] Orchestrator → Mock Executor → Node results
       ↓
[Chapter 4] PipelineRun → SQLite persistence → Query
       ↓
[Chapter 5] Multi-Scenario → 3 DAG types validated
```

## Running the Demo

```bash
cd /Users/lianwenhua/indie/Agents/hermes/projects/cinemate
source .venv/bin/activate

# Run all chapters (recommended)
python scripts/demo_mvp.py

# Run a specific chapter
python scripts/demo_mvp.py --chapter 1   # Intent Parsing
python scripts/demo_mvp.py --chapter 3   # Orchestrator Execution
python scripts/demo_mvp.py --chapter 5   # Multi-Scenario
```

## Chapter Details

### Chapter 1: Intent Parsing
**What it tests**: Natural language → DAG JSON conversion.
**Test cases**: 5 prompts in Chinese and English.
**Expected output**: Correct intent type (single_scene, product_ad, multi_scene) and node count.

### Chapter 2: DAG Construction
**What it tests**: DAG JSON → PipelineDAG with proper edge construction.
**Test cases**: Linear (3 nodes), Branching (4 nodes), Multi-scene (6 nodes).
**Expected output**: Correct node count, edge structure, and type propagation.

### Chapter 3: Orchestrator Execution
**What it tests**: Full DAG execution via Orchestrator with Mock executor.
**Flow**: Create run → Execute DAG → Verify all nodes succeed → Check SQLite persistence.
**Expected output**: Run status = COMPLETED, all 3 nodes executed, records in DB.

### Chapter 4: PipelineRun Lifecycle
**What it tests**: Complete run lifecycle with metadata.
**Flow**: Create run → Execute → Query history → Verify multiple runs.
**Expected output**: Run persists, status transitions correctly, DB contains multiple runs.

### Chapter 5: Multi-Scenario Validation
**What it tests**: All 3 DAG types execute successfully end-to-end.
**Scenarios**: Single scene (3 nodes), Ad pipeline (4 nodes), Multi-scene (6 nodes).
**Expected output**: All 3 scenarios complete with correct node counts.

## Architecture Validated

| Component | Status | Notes |
|-----------|--------|-------|
| Intent Parser | ✅ | Keyword-based (MVP), ready for LLM replacement |
| DAG Engine | ✅ | PipelineDAG with edge validation |
| Orchestrator | ✅ | Direct execution mode, FSM integration |
| Mock Provider | ✅ | Deterministic results, traceable outputs |
| Store (SQLite) | ✅ | CRUD, run persistence, node records |
| CLI | ✅ | create/status commands, mock default |
| Skills | ✅ | SkillStore + SkillIndexer (progressive disclosure) |

## Next Steps

1. **Replace Mock Intent Parser** with real DirectorAgent (DashScope Qwen)
2. **Add Real Providers** (Kling, Runway) for actual video generation
3. **Implement Artifact Storage** (CAS) for physical blob tracking
4. **Add Event-Driven Mode** (Redis Pub/Sub) for async execution

## Troubleshooting

- **ImportError**: Ensure `.venv` is activated and `pip install -e .` has been run.
- **SQLite lock**: Make sure no other process has the DB open.
- **Click not found**: Run `pip install click>=8.0.0` (should be in pyproject.toml).

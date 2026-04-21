# CineMate 🎬

> **AI Video Production OS**: Director Agent + Incremental Change Engine

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-21%20files-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](tests/)
[![Architecture](https://img.shields.io/badge/architecture-4.1%2F5-blue.svg)](docs/PMO/)

**[🌐 中文文档](README_zh.md)** | **[📊 Progress Report](docs/PMO/project_progress_report.md)** | **[📝 Sprint 3 Roadmap](docs/PMO/sprint3_roadmap.md)**

---

## 🎯 Vision

**To democratize filmmaking by safeguarding creative vision and empowering storytellers to produce at scale—ensuring technology amplifies artistry, never supersedes it.**

CineMate is an **AI Video Production Operating System** that brings software engineering practices to video creation. We believe the future of filmmaking lies not in replacing human creativity with automation, but in **amplifying creative potential through intelligent tooling**.

Unlike "one-click" black-box tools that obscure the creative process or complex node-based editors that require technical expertise, CineMate is:

- **Agent-Driven**: A Director Agent interprets natural language and orchestrates the entire pipeline—translating vision to execution while preserving creative intent
- **Version Controlled**: Git-like versioning for video assets ("Video Git")—empowering experimentation without fear of losing work
- **Incremental**: Only re-render changed nodes using Dirty Propagation—respecting both creative time and computational resources
- **Cloud-Native**: Local-first execution with cloud-brain orchestration—giving creators full ownership of their assets

> "Technology should serve the story, not dictate it. Manage video creation like you manage code—but keep the soul of filmmaking intact."

---

## ✨ Core Features

### 🎭 Director Agent
Natural language to video pipeline. Simply describe your vision:
```
"Create a cyberpunk video with neon lights and rain"
"Make it Wong Kar-wai style, slow motion"
"Add product close-up after the wide shot"
```

The Agent translates your intent into a DAG (Directed Acyclic Graph) of video operations.

### 🔄 Video Git
Every generation is a commit. Track history, branch experiments, and reuse assets:

```python
# Run 1: Initial generation
run_v1 = pipeline.run(prompt="Cyberpunk city")

# Run 2: Modify lighting (branches from v1)
run_v2 = pipeline.run(
    prompt="Warmer lighting",
    parent_run_id=run_v1.run_id  # Git-like branching
)

# Only changed nodes re-render
# Unchanged assets are symlinked (0-copy)
```

### ⚡ Incremental Engine
Smart dirty propagation using DAG topology:

```
Original:  A → B → C → D
Modified:      B'

Re-render:     B' → C' → D'
Reuse:    A (unchanged)
```

### 🧠 Skill System (Sprint 3 New)
Progressive disclosure for the Director Agent — reusable patterns and auto-generated skills:

```
User: "Create a cyberpunk video"
    ↓
DirectorAgent receives skill index:
  - style-cyberpunk: Neon lights, dark atmosphere...
  - workflow-short-ad: 5-step product ad template...
    ↓
Agent can load full skill content on-demand
    ↓
Execution learns from experience → SkillReviewer auto-generates new skills
```

**Skill Categories**:
- **STYLE**: Visual style strategies (cyberpunk, wong-kar-wai)
- **WORKFLOW**: Workflow templates (short-ad, product-review)
- **ERROR_RECOVERY**: Error patterns learned from failures
- **QUALITY**: Quality gating and evaluation

### 🖥️ CLI Commands (Sprint 3 New)
Full CLI for MVP video production:

```bash
# Create video from natural language
cinemate create "A cyberpunk city with neon lights"

# Apply a skill/style
cinemate create "Product ad for headphones" --style workflow-short-ad

# Interactive loop mode
cinemate loop

# Video Git commands
cinemate history              # Show run history
cinemate history --branch main --limit 10
cinemate history --run run_001  # Node-level details

cinemate diff run_002        # Compare with parent
cinemate diff run_002 --parent run_001

cinemate branches            # List all branches

# System status
cinemate status
```

### 🏗️ Async Infrastructure
Production-ready job queue for long-running video operations:
- **JobQueue**: Redis-backed queue with priority support
- **EventBus**: Pub/Sub for real-time updates
- **Workers**: Distributed execution across GPU clusters

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
│  CLI / Web / API                                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 DIRECTOR AGENT                              │
│  ReActAgent + Intent Parsing → DAG Construction             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              SKILL SYSTEM (Sprint 3)                  │  │
│  │  SkillStore + SkillIndexer + SkillLoader + Reviewer  │  │
│  │  Progressive disclosure + Auto-generation            │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   CORE ENGINE                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     DAG      │  │     FSM      │  │ Orchestrator │      │
│  │  (Topology)  │  │ (Lifecycle)  │  │ (Execution)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│               ASYNC INFRASTRUCTURE                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  JobQueue    │  │  EventBus    │  │   Workers    │      │
│  │  (Redis)     │  │ (Pub/Sub)    │  │  (RQ/Celery) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              PROVIDER ADAPTERS (Sprint 2)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Kling      │  │   Runway     │  │   Mock       │      │
│  │  Provider    │  │  Provider    │  │  Provider    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  Factory + Registry + Health Check + Cost Estimation        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              UPSTREAM APIs                                  │
│  OpenAI · Kling AI · Runway ML · Luma AI · Local GPU        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Redis 6.0+ (for async infrastructure)
- Docker (optional, for containerized Redis)

### Installation

```bash
# Clone repository
git clone https://github.com/lamwimham/cineMate.git
cd cineMate

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e ".[dev]"

# Start Redis (using Docker)
docker-compose -f docker-compose.infra.yml up -d redis
```

### Verify Installation

```bash
# Run tests
pytest

# Expected output:
# ===================== 121 passed in 3.42s ======================
# Coverage: core modules 96%+
```

---

## 📖 Usage

### 1. Basic Video Generation

```python
import asyncio
from cine_mate.agents.director_agent import DirectorAgent

async def main():
    # Initialize Agent
    agent = DirectorAgent(
        name="Director",
        model_config={"model_type": "openai", "model_name": "gpt-4"}
    )
    
    # Natural language to video
    result = await agent.chat(
        "Create a 5-second cyberpunk city scene with neon lights"
    )
    
    print(f"Run ID: {result.run_id}")
    print(f"Status: {result.status}")

asyncio.run(main())
```

### 2. Video Git Workflow

```python
from cine_mate.core.store import Store
from cine_mate.engine.orchestrator import Orchestrator
from cine_mate.engine.dag import PipelineDAG

async def video_git_workflow():
    store = Store("./cinemate.db")
    await store.init_db()
    
    # Create DAG: Script → Image → Video
    dag = PipelineDAG()
    dag.add_node("script", "text_generation", {"prompt": "Cyberpunk script"})
    dag.add_node("image", "image_generation", {"style": "neon"})
    dag.add_node("video", "video_generation", {"duration": 5})
    dag.add_edge("script", "image")
    dag.add_edge("image", "video")
    
    # Run 1: Initial
    run1 = PipelineRun(run_id="run_001", dag_snapshot=dag.to_dict())
    orch1 = Orchestrator(store, run1, dag, executor_fn=mock_executor)
    await orch1.execute()
    
    # Run 2: Modify image node (incremental)
    dag.add_node("image", "image_generation", {"style": "film_noir"})
    run2 = PipelineRun(
        run_id="run_002",
        parent_run_id="run_001",  # Git-like parent
        dag_snapshot=dag.to_dict()
    )
    
    # Only image → video re-render
    # Script node reused from run_001
    orch2 = Orchestrator(store, run2, dag, executor_fn=mock_executor)
    await orch2.execute()
```

### 3. Async Job Queue

```python
from cine_mate.infra.queue import JobQueue
from cine_mate.infra.event_bus import EventBus

async def async_pipeline():
    # Initialize infrastructure
    event_bus = EventBus("redis://localhost:6379")
    await event_bus.connect()
    
    queue = JobQueue(
        redis_url="redis://localhost:6379",
        event_bus=event_bus
    )
    await queue.connect()
    
    # Submit job
    job_id = await queue.submit_job(
        run_id="run_001",
        node_id="video_gen_01",
        job_type="image_to_video",
        params={
            "image_url": "https://...",
            "duration": 5,
            "motion_strength": 0.5
        },
        priority=1
    )
    
    # Subscribe to events
    await event_bus.subscribe(
        "node_completed",
        lambda e: print(f"Node {e.node_id} completed!")
    )
```

---

## 🏗️ Project Structure

```
cineMate/
├── cine_mate/                 # Main package
│   ├── agents/                # Director Agent & Tools
│   │   ├── director_agent.py  # ReActAgent implementation
│   │   └── tools/             # Agent tools (EngineTools)
│   ├── adapters/              # Provider adapters (Sprint 2)
│   │   ├── base.py            # BaseVideoProvider abstract class
│   │   ├── factory.py         # Provider registry & factory
│   │   ├── kling_provider.py  # Kling AI adapter
│   │   ├── runway_provider.py # Runway ML adapter
│   │   └── mock_provider.py   # Mock provider for testing
│   ├── config/                # Configuration system (Sprint 2)
│   │   ├── models.py          # Pydantic config models
│   │   ├── defaults.yaml      # Default config
│   │   └── loader.py          # Config loader
│   ├── core/                  # Core data models & storage
│   │   ├── models.py          # Pydantic models (Run, Node, Artifact)
│   │   └── store.py           # SQLite storage layer
│   ├── cli/                   # CLI commands (Sprint 3)
│   │   ├── main.py            # Click CLI entry point
│   │   ├── commands.py        # create/loop/status commands
│   │   └── video_git.py       # history/diff/branches commands
│   ├── engine/                # Execution engine
│   │   ├── dag.py             # DAG topology & dirty propagation
│   │   ├── fsm.py             # Node state machine
│   │   ├── orchestrator.py    # Pipeline execution
│   │   └── queue_integration.py # JobQueue-Engine integration
│   ├── infra/                 # Async infrastructure
│   │   ├── queue.py           # JobQueue (Redis)
│   │   ├── event_bus.py       # EventBus (Pub/Sub)
│   │   ├── schemas.py         # Event schemas
│   │   └── worker.py          # RQ workers
│   └── skills/                # Skill System (Sprint 3)
│       ├── models.py          # Skill metadata models
│       ├── skill_store.py     # SQLite + filesystem CRUD
│       ├── skill_indexer.py   # Progressive disclosure index
│       ├── skill_loader.py    # On-demand content loading
│       ├── skill_reviewer.py  # Hermes auto-generation
│       └── data/              # Skill files directory
│           ├── style-cyberpunk/SKILL.md
│           └── workflow-short-ad/SKILL.md
├── tests/                     # Test suite (~350 tests, 88% coverage)
│   ├── unit/                  # Unit tests
│   │   ├── adapters/          # Provider adapter tests
│   │   ├── cli/               # CLI command tests
│   │   ├── core/              # Store tests
│   │   ├── engine/            # DAG/FSM tests
│   │   ├── infra/             # Queue/EventBus tests
│   │   ├── skills/            # Skill system tests
│   │   └── config/            # Config loader tests
│   ├── integration/           # Integration tests (MVP Demo)
│   └── conftest.py            # Pytest fixtures
├── docs/                      # Documentation
│   ├── architecture.md        # System architecture
│   ├── adr/                   # Architecture Decision Records
│   ├── skills/                # Skill System docs (Sprint 3)
│   │   ├── user_guide.md      # Skill creation guide
│   │   └and api_reference.md   # Skill API reference
│   ├── PMO/                   # Project management
│   │   ├── project_progress_report.md
│   │   ├── sprint3_roadmap.md
│   │   └and sprint3_day2-6_plan.md
│   └and demo/                  # Demo guides
│       └and mvp_demo_guide.md
├── prompts/                   # LLM prompts
│   └── intent_v1.md           # Director Agent prompt
├── scripts/                   # Utility scripts
│   └and demo_mvp.py            # MVP E2E demo script
├── .github/workflows/         # CI/CD (GitHub Actions)
│   └and test.yml               # pytest + coverage workflow
├── pyproject.toml             # Project config
├── pytest.ini                 # Test configuration
├── README.md                  # English documentation
├── README_zh.md               # Chinese documentation
└and docker-compose.infra.yml   # Redis for local dev
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=cine_mate --cov-report=html
open htmlcov/index.html
```

### Run Specific Test Suite
```bash
pytest tests/unit/engine/test_dag.py -v
pytest tests/unit/engine/test_fsm.py -v
pytest tests/unit/core/test_store.py -v
```

### Current Test Status
| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| DAG | 42 | 97% | ✅ |
| FSM | 42 | 97% | ✅ |
| Store | 35 | 90% | ✅ |
| Provider Adapters | 53 | 86% | ✅ |
| Config Loader | 25 | 90% | ✅ |
| Queue Integration | 12 | 88% | ✅ |
| EventBus | 15 | 85% | ✅ |
| SkillStore | 29 | 95% | ✅ |
| SkillLoader | 14 | 92% | ✅ |
| SkillReviewer | 15 | 93% | ✅ |
| CLI Commands | 25 | 88% | ✅ |
| Video Git | 21 | 90% | ✅ |
| Integration Tests | 8 | 85% | ✅ |
| **Total** | **~350 tests** | **88%** | ✅ |

### CI/CD Status
| Component | Status | Note |
|-----------|--------|------|
| GitHub Actions | ✅ | Multi-Python (3.11, 3.12) |
| pytest + coverage | ✅ | Coverage >80% required |
| Redis container | ✅ | docker-compose.infra.yml |

---

## 🤝 Contributing

We follow a structured development workflow:

### Branch Naming
```
feature/sprint{N}-{description}
fix/{issue-id}-{description}
docs/{description}
```

### Commit Convention
```
type(scope): description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- test: Tests
- refactor: Code refactoring

Examples:
feat(agents): add DirectorAgent skeleton
test(engine): add DAG dirty propagation tests
docs(adr): add Job Queue decision record
```

### Development Workflow
1. Create feature branch from `main`
2. Develop with tests
3. Submit PR with description
4. Code review by PM + peer
5. Merge to `main`

### Team
- **hermes**: Agent & Gateway Lead
- **copaw**: Infrastructure & Async Lead
- **claude**: QA & Testing Lead
- **PM**: Project Management (AI Assistant)

---

## 📋 Roadmap

### Sprint 1 (Completed) ✅
- [x] Core Engine (DAG, FSM, Orchestrator)
- [x] AgentScope Integration (DirectorAgent)
- [x] Async Infrastructure (JobQueue, EventBus)
- [x] Testing Framework (21 files, 6,593 lines, 85% coverage)
- [x] Event-Driven Orchestrator (node_completed trigger)
- [x] Configuration System Skeleton (multi-model profiles)

**Result**: ✅ **GO** - AgentScope + Engine integration validated

### Sprint 2 (Completed) ✅
**Target**: Provider Integration + CI/CD + Test Coverage

| Day | Focus | Status |
|-----|-------|--------|
| Day 1 | CI/CD GitHub Actions | ✅ Done |
| Day 2 | Config system + Coverage expansion | ✅ Done |
| Day 3 | Provider adapter pattern (Kling, Runway, Mock) | ✅ Done |
| Day 4 | Integration tests + Coverage report | ✅ Done |

**Key Deliverables**:
- [x] Provider Adapter Architecture (BaseVideoProvider, Factory, Registry)
- [x] Kling & Runway Provider implementations
- [x] Mock Provider for testing without API keys
- [x] CI/CD with GitHub Actions (multi-Python)
- [x] Test coverage: 85% (target >80%)
- [x] Architecture Health Score: 4.1/5

### Sprint 3 (Completed) ✅
**Target**: Skill System + CLI + MVP Readiness

| Issue | Focus | Status |
|-------|-------|--------|
| #34 | SkillStore + SkillIndexer | ✅ Merged (PR #43) |
| #35 | MVP CLI Entry Point | ✅ Merged (PR #44) |
| #36 | SkillLoader + DirectorAgent | ✅ Merged (PR #46) |
| #37 | MVP E2E Demo | ✅ Merged (PR #45) |
| #38 | SkillReviewer Auto-generation | ✅ Merged (PR #47) |
| #39 | Video Git CLI | ✅ Merged (PR #48) |

**Key Deliverables**:
- [x] SkillStore: SQLite + filesystem CRUD, YAML frontmatter validation
- [x] SkillIndexer: Progressive disclosure index (name + description only)
- [x] SkillLoader: OpenCode XML pattern for on-demand loading
- [x] SkillReviewer: Hermes auto-generation from PipelineRun analysis
- [x] CLI Commands: create/loop/status/history/diff/branches
- [x] Video Git: Git-like version control for video assets
- [x] MVP Demo: Full pipeline validation (NL → Intent → DAG → Orchestrator)

**Test Results**:
- SkillStore: 29/29 ✅
- SkillLoader: 14/14 ✅
- SkillReviewer: 15/15 ✅
- CLI: 25/25 ✅
- Video Git: 21/21 ✅
- Integration: 8/8 ✅

### Sprint 4 (Planning) ⏳
**Target**: MVP Release

- [ ] Web UI (Video Git visualization)
- [ ] Real API validation (Kling/Runway)
- [ ] Production hardening
- [ ] MVP Release

### Future Sprints
- [ ] Human-in-the-Loop (HITL) Support
- [ ] Production deployment

---

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [Async Interface Spec](docs/architecture/async_interface.md)
- [ADR-001: Job Queue](docs/adr/ADR-001_job_queue.md)
- [Agent Prompt Template](prompts/intent_v1.md)
- [Project Progress Report](docs/PMO/project_progress_report.md)
- [Sprint 2 Test Coverage Report](docs/testing/sprint2_coverage_report.md)
- [Sprint 3 Roadmap](docs/PMO/sprint3_roadmap.md)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Agent Framework | AgentScope |
| API Framework | FastAPI |
| Database | SQLite (local), PostgreSQL (cloud) |
| Queue | Redis + RQ |
| Events | Redis Pub/Sub |
| Testing | pytest + pytest-asyncio |
| Linting | ruff |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- Inspired by Git's version control model
- Agent architecture based on ReAct pattern
- Event-driven design patterns from Domain-Driven Design

---

<p align="center">
  <strong>CineMate</strong> — Where Video Meets Engineering
</p>

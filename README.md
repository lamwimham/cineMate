# CineMate 🎬

> **AI Video Production OS**: Director Agent + Incremental Change Engine

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-121%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-47%25-yellow.svg)](tests/)

**[🌐 中文文档](README_zh.md)** | **[📝 Sprint 1 Progress](docs/PMO/sprint_1_progress.md)**

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
│              UPSTREAM PROVIDERS                             │
│  OpenAI · Kling · Runway · Local GPU Cluster                │
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
│   ├── core/                  # Core data models & storage
│   │   ├── models.py          # Pydantic models (Run, Node, Artifact)
│   │   └── store.py           # SQLite storage layer
│   ├── engine/                # Execution engine
│   │   ├── dag.py             # DAG topology & dirty propagation
│   │   ├── fsm.py             # Node state machine
│   │   └── orchestrator.py    # Pipeline execution
│   └── infra/                 # Async infrastructure
│       ├── queue.py           # JobQueue (Redis)
│       ├── event_bus.py       # EventBus (Pub/Sub)
│       ├── schemas.py         # Event schemas
│       └── worker.py          # RQ workers
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   │   ├── core/              # Store tests
│   │   └── engine/            # DAG/FSM tests
│   ├── integration/           # Integration tests
│   └── conftest.py            # Pytest fixtures
├── docs/                      # Documentation
│   ├── architecture.md        # System architecture
│   ├── adr/                   # Architecture Decision Records
│   └── PMO/                   # Project management
├── prompts/                   # LLM prompts
│   └── intent_v1.md           # Director Agent prompt
├── pyproject.toml             # Project config
├── pytest.ini                 # Test configuration
└── docker-compose.infra.yml   # Redis for local dev
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
| DAG | 42 | 100% | ✅ |
| FSM | 42 | 97% | ✅ |
| Store | 35 | 100% | ✅ |
| Models | 2 | 100% | ✅ |
| **Total** | **121** | **47%** | ✅ |

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

### Sprint 1 (Current) ✅
- [x] Core Engine (DAG, FSM, Orchestrator)
- [x] AgentScope Integration (DirectorAgent)
- [x] Async Infrastructure (JobQueue, EventBus)
- [x] Testing Framework (121 tests, 96% core coverage)

### Sprint 2 (Next)
- [ ] Cloud Gateway (Auth, Billing, Proxy)
- [ ] Skill System (Wong Kar-wai, Cyberpunk styles)
- [ ] CI/CD Pipeline (GitHub Actions)
- [ ] CLI Interface

### Sprint 3
- [ ] Web UI (Video Git visualization)
- [ ] Multi-Provider Routing (Kling, Runway, etc.)
- [ ] Production Hardening

---

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [Async Interface Spec](docs/architecture/async_interface.md)
- [ADR-001: Job Queue](docs/adr/ADR-001_job_queue.md)
- [Agent Prompt Template](prompts/intent_v1.md)

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

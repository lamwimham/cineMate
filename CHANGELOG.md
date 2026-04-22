# Changelog

All notable changes to CineMate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-04-22

### 🎉 MVP Release

First public release of CineMate - AI Video Production OS.

### ✨ Features

#### Core Engine
- **DAG Engine**: Directed Acyclic Graph for video production workflow
- **FSM State Machine**: Finite State Machine for node execution control
- **Orchestrator**: Central coordinator for workflow execution
- **Video Git**: Content-addressable storage for video version control
- **Dirty Propagation**: Incremental change tracking

#### Infrastructure
- **JobQueue**: Redis + RQ based async job queue
- **EventBus**: Redis Pub/Sub for real-time event broadcasting
- **Worker**: Distributed worker for job execution

#### Provider Adapters
- **KlingProvider**: Kling AI video generation (text-to-video, image-to-video)
- **RunwayProvider**: Runway ML Gen-4 video generation
- **MockProvider**: Mock provider for testing
- **Provider Factory**: Dynamic provider selection with fallback

#### Director Agent
- **DirectorAgent**: AI-powered video creation assistant
- **Skill System**: Progressive disclosure pattern for skill management
  - SkillStore: Skill storage and retrieval
  - SkillIndexer: Skill indexing for fast lookup
  - SkillLoader: On-demand skill loading
  - SkillReviewer: Hermes auto-generation from PipelineRun

#### Web UI
- **React + TypeScript**: Modern frontend framework
- **Chat + Canvas**: Split-screen layout for conversation and video preview
- **DAG Visualization**: Real-time workflow progress visualization
- **Video Git Panel**: Version tree and history viewer
- **Tauri Integration**: Lightweight desktop application

#### API & CLI
- **FastAPI Server**: RESTful API with 5 endpoints
- **WebSocket**: Real-time progress broadcasting (2 endpoints)
- **CLI Tool**: Command-line interface for video creation
  - `cinemate create`: Create video from natural language
  - `cinemate loop`: Interactive creation mode
  - `cinemate status`: View run status
  - `cinemate history`: View creation history
  - `cinemate diff`: Compare video versions
  - `cinemate branches`: Manage Video Git branches

### 📚 Documentation

- **Architecture Documentation**: System design and components
- **ADR-001-003**: Architecture Decision Records
- **API Reference**: Complete API documentation
- **Skill User Guide**: Skill creation and usage guide
- **API Key Configuration**: API key setup guide
- **Frontend Architecture**: Tauri + React design
- **Design System**: UI/UX design specification
- **User Manual**: End-user guide
- **MVP Demo Script**: Demo presentation script

### 🧪 Testing

- **Unit Tests**: 129+ tests across all modules
- **Integration Tests**: Web API (18/18), E2E user flow (5/13)
- **Real API Tests**: Kling + Runway validation tests
- **Test Coverage**: ~77% overall

### 🔧 Configuration

- **Multi-environment Support**: Development, staging, production
- **API Key Management**: Environment variables, .env, config file
- **Provider Configuration**: Primary/fallback provider selection

### 🚀 Known Limitations

- E2E tests: 5/13 passed (async database write issue, to be optimized in Sprint 5)
- Docker support: Not yet implemented
- User authentication: Not included in MVP
- Billing system: Not included in MVP
- HITL (Human-in-the-Loop): Planned for Sprint 5

---

## Future Releases

### [0.2.0] - Planned Sprint 5-6

- HITL (Human-in-the-Loop) support
- Email/Slack notifications
- Approval queue UI
- E2E test optimization
- Docker support

### [0.3.0] - Planned Sprint 7+

- User authentication
- Multi-tenant support
- Billing system
- Advanced editing features
- Mobile application

---

## Sprint History

| Sprint | Duration | Focus | Status |
|--------|----------|-------|--------|
| Sprint 1 | 2026-04-01~06 | Core Engine + AgentScope | ✅ Complete |
| Sprint 2 | 2026-04-07~13 | Provider Adapters + Tests + CI/CD | ✅ Complete |
| Sprint 3 | 2026-04-14~20 | Skill System + CLI + MVP Demo | ✅ Complete |
| Sprint 4 | 2026-04-21~26 | Web UI + Real API + MVP Prep | ✅ Complete |

---

## Contributors

- **Hermes**: Agent/Gateway/Web development
- **Copaw**: Infra/Skill/Testing development
- **Claude**: QA/Documentation support
- **PM (Qwen)**: Project management + Sprint planning

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Release Date**: 2026-04-22
**Release Author**: PM (Qwen)
**Release Type**: MVP (Minimum Viable Product)
# CineMate Implementation Plan

> **Version**: 1.0.0
> **Based on**: `architecture.md` (v0.2.0) & `agentscope_guide.md`

## 🏁 Milestone 1: Core Engine & Video Git (Phase 1-2)
> **Status**: ✅ **COMPLETED**
> **Goal**: Verified Local DAG/FSM Engine, Content-Addressable Store (CAS), and Dirty Propagation.

*   **[Done]** `cine_mate/core`: `models.py` (Run, Artifact, Blob) and `store.py` (SQLite/AsyncIO).
*   **[Done]** `cine_mate/engine`: `dag.py` (Topology), `fsm.py` (Lifecycle), `orchestrator.py` (Execution).
*   **[Done]** `tests`: `test_dirty_propagation.py` passed (Node Reuse & Replay logic).

---

## 🚀 Milestone 2: AgentScope Integration (Phase 4.1)
> **Status**: 🔜 **NEXT**
> **Est**: 3 Days
> **Goal**: Integrate CineMate Engine with **AgentScope 1.0**, enabling Natural Language -> Engine Control.

### Task 2.1: Project Setup & AgentScope Init
*   **Objective**: Initialize AgentScope environment.
*   **Files**:
    *   `pyproject.toml`: Add `agentscope>=1.0.0`.
    *   `cine_mate/agents/`: Create `director_agent.py`.
*   **Steps**:
    1.  Create `DirectorAgent` inheriting from `ReActAgent`.
    2.  Configure Mock Model (for local testing without Cloud Gateway).

### Task 2.2: Engine-to-Toolkit Bridge
*   **Objective**: Wrap DAG Engine into AgentScope `Toolkit`.
*   **Files**:
    *   `cine_mate/agents/tools/engine_tools.py`.
*   **Key Tools**:
    *   `create_pipeline(prompt: str)`: Create new Run.
    *   `get_run_status(run_id: str)`: Check progress.
    *   `modify_node(node_id: str, params: dict)`: Trigger Dirty Propagation.

### Task 2.3: Intent Parsing & Orchestration
*   **Objective**: Verify Agent translates NL to Engine Actions.
*   **Steps**:
    1.  Write System Prompt: "You are a Director Agent controlling CineMate..."
    2.  **Test**: Input "Create a cyberpunk video" -> Agent calls `create_pipeline`.

---

## ☁️ Milestone 3: Cloud Gateway MVP (Phase 3)
> **Est**: 4 Days
> **Goal**: Build Server Gateway, Auth, Billing, and Routing.

### Task 3.1: FastAPI Server Skeleton
*   **Objective**: Basic Server Setup.
*   **Files**: `server/main.py`, `server/routers/jobs.py`.
*   **Steps**:
    1.  Init FastAPI.
    2.  Implement `POST /api/v1/jobs`.

### Task 3.2: Auth & Billing Middleware
*   **Objective**: Managed vs BYOK Billing.
*   **Files**: `server/middleware/auth.py`, `server/services/billing.py`.
*   **Steps**:
    1.  **Managed**: Check credits -> Pre-deduct.
    2.  **BYOK**: Verify `X-BYOK-Signature` (Hash match).

### Task 3.3: Proxy & Mock Upstream
*   **Objective**: Route requests to Upstream (Mock).
*   **Files**: `server/services/proxy.py`.
*   **Steps**:
    1.  Receive Job -> Route based on `model_type`.
    2.  **Audit**: Log Request/Response to `audit_logs`.

---

## 🎨 Milestone 4: Style as Skill System (Phase 4.2)
> **Est**: 3 Days
> **Goal**: Implement Anthropic-style Skill Loading.

### Task 4.1: Skill Loader
*   **Objective**: Parse `SKILL.md` and `config.yaml`.
*   **Files**: `cine_mate/skills/loader.py`.
*   **Steps**:
    1.  Load YAML Frontmatter (Name, Version).
    2.  Extract Markdown Body for Agent Prompt.

### Task 4.2: Agent Dynamic Injection
*   **Objective**: Dynamic Skill Loading at Runtime.
*   **Files**: `cine_mate/agents/director_agent.py`.
*   **Steps**:
    1.  User: "Use Wong Kar-wai style".
    2.  Agent calls `load_skill` -> Updates System Prompt.

### Task 4.3: Engine Overrides
*   **Objective**: Apply `config.yaml` parameters to DAG.
*   **Files**: `cine_mate/engine/orchestrator.py`.
*   **Steps**:
    1.  Merge `default_params` + `skill_overrides` + `user_params`.

---

## 🖥️ Milestone 5: CLI & UI (Phase 5)
> **Est**: 3 Days
> **Goal**: User Interface & Video Git Visualization.

### Task 5.1: CLI Chat Interface
*   **Objective**: `cinemate chat`.
*   **Files**: `cine_mate/cli.py`.
*   **Steps**:
    1.  REPL Loop: Input -> Agent -> Output.

### Task 5.2: Video Git Visualization
*   **Objective**: `cinemate log`.
*   **Steps**:
    1.  Query `pipeline_runs`.
    2.  Render Tree (like `git log --graph`) using `rich`.

---

## 🚦 Immediate Action
**Start Milestone 2 (AgentScope Integration)**.
*   **Why**: Validates the core "User -> Agent -> Engine" loop locally without waiting for the Server (Milestone 3).

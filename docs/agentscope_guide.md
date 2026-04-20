# AgentScope Integration Guide (CineMate)

> **Official Docs**: https://doc.agentscope.io/
> **Version**: AgentScope 1.0+

This guide explains how to use **AgentScope** to build the **Director Agent** for CineMate.

## 1. Core Concepts & CineMate Mapping

| AgentScope Component | CineMate Role | Description |
| :--- | :--- | :--- |
| **`ReActAgent`** | **Director Agent** | The main agent that receives user input, parses intent, and decides which tools to call (e.g., `create_video`, `modify_lighting`). |
| **`Toolkit`** | **Video Engine Bridge** | A collection of tools wrapping CineMate's DAG Engine. Tools like `run_pipeline`, `get_artifact_status`, `change_prompt`. |
| **`Msg` (Message)** | **Command / Event** | Communication between User and Agent. Can contain text, images, or structured JSON (e.g., DAG snapshots). |
| **`Memory`** | **Video Context** | Stores the conversation history and **current pipeline state** (e.g., "Currently working on Run #1, Scene 3"). |
| **`Model`** | **Cloud Brain** | Interface to the LLM (via CineMate Cloud Gateway). Handles prompt formatting and API calls. |
| **`Pipeline`** | **Workflow** | Orchestration of multiple agents (e.g., ScriptWriter Agent -> VisualDirector Agent). |

---

## 2. Architecture Design

### 2.1 Directory Structure

```text
cine_mate/
└── agents/
    ├── __init__.py
    ├── director_agent.py      # The main ReActAgent subclass
    ├── video_tools.py         # Toolkit wrapping DAG Engine
    └── skills/                # AgentScope Skills (Style definitions)
        └── wong_kar_wai.py
```

### 2.2 Implementation Pattern

#### Step 1: Define the Toolkit (Video Tools)
The Agent needs tools to interact with the local engine.

```python
from agentscope.tool import Toolkit, ToolResponse
from cine_mate.engine import Orchestrator

def create_video_tool(orchestrator: Orchestrator):
    async def execute(prompt: str, style: str = None) -> ToolResponse:
        # 1. Parse intent -> DAG config
        # 2. Call Orchestrator.run()
        # 3. Return result Msg
        return ToolResponse(content=Msg(name="system", content="Video generation started..."))
    
    return execute
```

#### Step 2: Initialize the Agent
Use `ReActAgent` for the Director.

```python
from agentscope.agent import ReActAgent
from agentscope.model import DashScopeChatModel # Or custom CineMate Model
from agentscope.memory import InMemoryMemory

async def main():
    # 1. Setup Model (Connect to CineMate Cloud Gateway)
    model = DashScopeChatModel(
        model_name="qwen-max",
        api_key="YOUR_KEY", # In reality, this is proxied
    )

    # 2. Setup Toolkit
    toolkit = Toolkit()
    toolkit.register_tool_function(create_video_tool(orchestrator))

    # 3. Create Agent
    director = ReActAgent(
        name="Director",
        sys_prompt="You are a professional video director. You control the CineMate engine.",
        model=model,
        memory=InMemoryMemory(),
        toolkit=toolkit,
    )

    # 4. Run
    msg = Msg(name="user", content="Make a cyberpunk video.")
    response = await director(msg)
```

---

## 3. Key Features for CineMate

### 3.1 Dynamic Tool Provisioning
CineMate allows users to switch "Skills" (Styles). We should dynamically load tools/skills based on the active style.
*   **Official Doc**: [Tool](https://doc.agentscope.io/tutorial/task_tool.html)
*   **Usage**: When a user selects "Wong Kar-wai Style", the Agent loads the `wong_kar_wai` skill which injects specific prompt suffixes into the tools.

### 3.2 Long-Term Memory (Video Git)
The Agent needs to remember past runs to support "Modify Scene 2".
*   **Official Doc**: [Long-Term Memory](https://doc.agentscope.io/tutorial/task_long_term_memory.html)
*   **Usage**: Use a custom memory implementation that retrieves context from CineMate's **SQLite Store** based on `run_id`.

### 3.3 Structured Output
To control the DAG Engine precisely, the Agent must output **JSON** (e.g., `{"action": "modify_node", "node_id": "img_02", "params": {...}}`).
*   **Official Doc**: [Prompt Formatter](https://doc.agentscope.io/tutorial/task_prompt.html)
*   **Usage**: Use `format_map` or structured output constraints in the Model wrapper to enforce JSON responses.

---

## 4. Quickstart Reference

For full details, refer to the official tutorials:
1.  **Installation**: `pip install agentscope`
2.  **Create ReAct Agent**: [Link](https://doc.agentscope.io/tutorial/quickstart_agent.html)
3.  **Tool Use**: [Link](https://doc.agentscope.io/tutorial/task_tool.html)
4.  **Memory**: [Link](https://doc.agentscope.io/tutorial/task_memory.html)
5.  **Pipeline**: [Link](https://doc.agentscope.io/tutorial/task_pipeline.html)

"""
CineMate Director Agent (AgentScope 1.0)
Task 2.3 Implementation

P0 Fix: Dependency injection for model + mock_mode support (closes #4)
Sprint 2: Real DashScope API call + API Key validation
"""

import os
import json
from typing import Optional

from agentscope.agent import ReActAgent
from agentscope.model import DashScopeChatModel
from agentscope.memory import InMemoryMemory
from agentscope.formatter import DashScopeChatFormatter

from cine_mate.agents.tools.engine_tools import EngineTools

# Load system prompt from file
# director_agent.py is in cine_mate/agents/
# prompts/ is in project root (2 levels up)
PROMPT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "intent_v1.md")
)


class MockChatModel:
    """Mock model for testing without API keys (Issue #4)"""
    
    model_name = "mock"
    stream = False
    
    async def __call__(self, *args, **kwargs):
        from agentscope.message import Msg
        return Msg(
            name="assistant",
            content=[{
                "type": "text",
                "text": json.dumps({
                    "intent": "Mock video request",
                    "nodes": [
                        {"id": "node_script", "type": "script_gen", "parents": []},
                        {"id": "node_image", "type": "text_to_image", "parents": ["node_script"]},
                        {"id": "node_video", "type": "image_to_video", "parents": ["node_image"]}
                    ]
                })
            }],
            role="assistant"
        )


def load_system_prompt() -> str:
    """Load the intent parsing prompt template."""
    try:
        with open(PROMPT_PATH, 'r') as f:
            content = f.read()
            if "## System Prompt" in content:
                prompt_part = content.split("## System Prompt")[1]
                if prompt_part.startswith("```"):
                    prompt_part = prompt_part[3:]
                if prompt_part.endswith("```"):
                    prompt_part = prompt_part[:-3]
                return prompt_part.strip()
            return content
    except Exception as e:
        print(f"Warning: Could not load prompt file. Using fallback. Error: {e}")
        return "You are a helpful assistant."


class DirectorAgent(ReActAgent):
    """
    The main Director Agent for CineMate.
    Responsible for parsing user intent, planning DAGs, and controlling the Engine.
    
    Supports:
    - Dependency injection for model
    - Mock mode for testing (no API key)
    - Real DashScope API call (default)
    - API Key validation at init time
    """

    def __init__(
        self,
        name: str = "Director",
        model_name: str = "qwen-max",
        api_key: Optional[str] = None,
        engine_tools: Optional[EngineTools] = None,
        use_mock: bool = False,
        model=None  # Dependency injection for model
    ):
        # 1. Setup Model
        if use_mock:
            model = MockChatModel()
        elif model is not None:
            pass  # Use injected model
        else:
            # Real DashScope (Qwen) - Sprint 2: with API Key validation
            resolved_api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
            if not resolved_api_key:
                raise ValueError(
                    "DASHSCOPE_API_KEY not set. "
                    "Please set the environment variable or pass api_key parameter. "
                    "Alternatively, use use_mock=True for testing without API."
                )
            model = DashScopeChatModel(
                model_name=model_name,
                api_key=resolved_api_key,
            )

        # 2. Load System Prompt
        sys_prompt = load_system_prompt()

        # 3. Setup Toolkit
        toolkit = None
        if engine_tools:
            from agentscope.tool import Toolkit
            toolkit = Toolkit()
            toolkit.register_tool_function(engine_tools.create_video)
            toolkit.register_tool_function(engine_tools.get_run_status)
            toolkit.register_tool_function(engine_tools.get_run_list)
            toolkit.register_tool_function(engine_tools.submit_plan)

        # 4. Initialize ReActAgent
        super().__init__(
            name=name,
            sys_prompt=sys_prompt,
            model=model,
            formatter=DashScopeChatFormatter(),
            toolkit=toolkit,
            memory=InMemoryMemory(),
        )

"""
CineMate Director Agent (AgentScope 1.0)
Task 2.3 Implementation

P0 Fix: Dependency injection for model + mock_mode support (closes #4)
Sprint 2: Real DashScope API call + API Key validation
Sprint 3: Skill System integration (progressive disclosure via SkillLoader)
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
    - Skill System integration (progressive disclosure)
    """

    def __init__(
        self,
        name: str = "Director",
        model_name: str = "qwen-max",
        api_key: Optional[str] = None,
        engine_tools: Optional[EngineTools] = None,
        use_mock: bool = False,
        model=None,  # Dependency injection for model
        skill_indexer=None,   # SkillIndexer for system prompt injection
        skill_loader=None,    # SkillLoader for on-demand content loading
    ):
        # 1. Setup Model (Priority: injected model > use_mock > default)
        if model is not None:
            pass  # Use injected model (highest priority)
        elif use_mock:
            model = MockChatModel()
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

        # 2. Load System Prompt (with optional skill index injection)
        sys_prompt = load_system_prompt()
        self._skill_loader = skill_loader  # Store for async inject_skills

        if skill_indexer:
            # Note: Skill index injection is done async via inject_skills()
            # to avoid event loop conflicts when called from async context.
            # If called synchronously, we try best-effort.
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                # We're in async context — store for later injection
                self._pending_skill_indexer = skill_indexer
            except RuntimeError:
                # No running loop — safe to run sync
                try:
                    index_entries = asyncio.run(skill_indexer.scan())
                    skill_section = skill_indexer.format_for_prompt(index_entries)
                    sys_prompt = f"{sys_prompt}\n\n{skill_section}"
                except Exception as e:
                    print(f"Warning: Could not load skill index. Error: {e}")

        # 3. Setup Toolkit
        toolkit = None
        if engine_tools:
            from agentscope.tool import Toolkit
            toolkit = Toolkit()
            toolkit.register_tool_function(engine_tools.create_video)
            toolkit.register_tool_function(engine_tools.get_run_status)
            toolkit.register_tool_function(engine_tools.get_run_list)
            toolkit.register_tool_function(engine_tools.submit_plan)

            # Register load_skill tool if skill_loader is provided
            if skill_loader:
                from cine_mate.agents.tools.skill_tool import make_load_skill_tool
                toolkit.register_tool_function(make_load_skill_tool(skill_loader))

        # 4. Initialize ReActAgent
        super().__init__(
            name=name,
            sys_prompt=sys_prompt,
            model=model,
            formatter=DashScopeChatFormatter(),
            toolkit=toolkit,
            memory=InMemoryMemory(),
        )
    
    async def inject_skills(self):
        """
        Inject skill index into system prompt (async-safe).
        
        Call this after agent creation when skill_indexer was provided
        but couldn't be injected during __init__ due to event loop conflicts.
        """
        indexer = getattr(self, '_pending_skill_indexer', None)
        if indexer is None:
            return
        
        try:
            index_entries = await indexer.scan()
            skill_section = indexer.format_for_prompt(index_entries)
            # _sys_prompt is the internal storage (sys_prompt is read-only property)
            self._sys_prompt = f"{self._sys_prompt}\n\n{skill_section}"
            del self._pending_skill_indexer
        except Exception as e:
            print(f"Warning: Could not inject skills. Error: {e}")

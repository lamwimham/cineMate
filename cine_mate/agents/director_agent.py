"""
CineMate Director Agent (AgentScope 1.0)
Task 2.3 Implementation
"""

import os
import asyncio
import json
from typing import Optional

from agentscope.agent import ReActAgent
from agentscope.model import DashScopeChatModel
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg

from cine_mate.agents.tools.engine_tools import EngineTools, register_engine_tools

# Load system prompt from file
# director_agent.py is in cine_mate/agents/
# prompts/ is in project root (2 levels up)
PROMPT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "intent_v1.md")
)

def load_system_prompt() -> str:
    """Load the intent parsing prompt template."""
    try:
        with open(PROMPT_PATH, 'r') as f:
            content = f.read()
            # Extract the prompt inside the code blocks if necessary, or return full
            # The file structure has "## System Prompt" followed by a code block.
            # We should extract that block to avoid cluttering the context with metadata.
            start_marker = "```\n"
            end_marker = "```"
            
            # Simple extraction logic
            # The prompt starts after the first occurrence of "## System Prompt"
            # Let's look for the content inside the markdown block
            
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
    """

    def __init__(
        self,
        name: str = "Director",
        model_name: str = "qwen-max",
        api_key: Optional[str] = None,
        engine_tools: Optional[EngineTools] = None,
        use_mock: bool = False
    ):
        # 1. Setup Model
        if use_mock:
            # For testing without API keys
            model_config = {
                "model_type": "post_api_chat",
                "config_name": "mock_model",
                "api_url": "http://mock-api", 
                "headers": {},
                "messages_key": "messages"
            }
            # We need to mock this or use a placeholder. 
            # For now, let's just require a real model or raise if needed.
            # In a real test, we might inject a mock model.
            raise NotImplementedError("Mock model implementation pending. Please provide API Key.")
        else:
            # Default to DashScope (Qwen) as per project config
            model = DashScopeChatModel(
                model_name=model_name,
                api_key=api_key or os.getenv("DASHSCOPE_API_KEY"),
            )

        # 2. Load System Prompt
        sys_prompt = load_system_prompt()

        # 3. Setup Toolkit
        toolkit = None
        if engine_tools:
            from agentscope.tool import Toolkit
            toolkit = Toolkit()
            # Register tools from the manager
            toolkit.register_tool_function(engine_tools.create_video)
            toolkit.register_tool_function(engine_tools.get_run_status)
            toolkit.register_tool_function(engine_tools.get_run_list)
            
            # Add a new tool for submitting the full DAG plan
            toolkit.register_tool_function(engine_tools.submit_plan)

        # 4. Initialize ReActAgent
        super().__init__(
            name=name,
            sys_prompt=sys_prompt,
            model=model,
            toolkit=toolkit,
            memory=InMemoryMemory(),
        )

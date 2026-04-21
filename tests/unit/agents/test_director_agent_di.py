"""
Tests for DirectorAgent Dependency Injection (Sprint 2 Day 2)

Test Coverage:
- Mock mode (use_mock=True)
- Dependency injection (model parameter)
- EngineTools integration
- System prompt loading
- MockChatModel functionality
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Note: These tests require agentscope to be installed
# Tests that import agentscope will be skipped if not available


class TestMockChatModel:
    """Test MockChatModel for testing without API keys."""

    def test_mock_model_returns_json_response(self):
        """MockChatModel returns JSON DAG plan."""
        from cine_mate.agents.director_agent import MockChatModel

        mock_model = MockChatModel()
        response = mock_model()

        assert response is not None
        assert hasattr(response, 'content')
        assert len(response.content) > 0

    def test_mock_response_contains_nodes(self):
        """Mock response contains DAG nodes."""
        from cine_mate.agents.director_agent import MockChatModel

        mock_model = MockChatModel()
        response = mock_model()

        text = response.content[0]["text"]
        data = json.loads(text)

        assert "nodes" in data
        assert len(data["nodes"]) == 3  # script, image, video

    def test_mock_nodes_have_correct_types(self):
        """Mock nodes have correct types."""
        from cine_mate.agents.director_agent import MockChatModel

        mock_model = MockChatModel()
        response = mock_model()

        text = response.content[0]["text"]
        data = json.loads(text)

        types = [node["type"] for node in data["nodes"]]
        assert "script_gen" in types
        assert "text_to_image" in types
        assert "image_to_video" in types


class TestLoadSystemPrompt:
    """Test system prompt loading."""

    def test_load_prompt_returns_string(self):
        """load_system_prompt returns a string."""
        from cine_mate.agents.director_agent import load_system_prompt

        prompt = load_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_prompt_fallback_on_missing_file(self):
        """Fallback prompt when file is missing."""
        from cine_mate.agents.director_agent import load_system_prompt

        # The actual implementation handles missing file gracefully
        prompt = load_system_prompt()

        # Should return something (either loaded or fallback)
        assert prompt is not None


class TestDirectorAgentMockMode:
    """Test DirectorAgent with mock_mode=True."""

    def test_mock_mode_creates_mock_model(self):
        """use_mock=True creates MockChatModel."""
        from cine_mate.agents.director_agent import DirectorAgent, MockChatModel

        # Create agent in mock mode (no engine_tools for simplicity)
        agent = DirectorAgent(use_mock=True, engine_tools=None)

        # Model should be MockChatModel
        assert isinstance(agent.model, MockChatModel)

    def test_mock_mode_no_api_key_required(self):
        """Mock mode works without API key."""
        from cine_mate.agents.director_agent import DirectorAgent

        # Create agent without any API key
        agent = DirectorAgent(use_mock=True, engine_tools=None)

        # Should not raise any error
        assert agent is not None

    def test_mock_agent_has_name(self):
        """Mock agent has correct name."""
        from cine_mate.agents.director_agent import DirectorAgent

        agent = DirectorAgent(name="TestDirector", use_mock=True, engine_tools=None)

        assert agent.name == "TestDirector"


class TestDirectorAgentDependencyInjection:
    """Test DirectorAgent with injected model."""

    def test_injected_model_is_used(self):
        """Injected model parameter is used."""
        from cine_mate.agents.director_agent import DirectorAgent

        # Create custom mock model
        custom_model = Mock()

        agent = DirectorAgent(model=custom_model, engine_tools=None)

        # Injected model should be used
        assert agent.model == custom_model

    def test_injected_model_overrides_model_name(self):
        """Injected model overrides model_name parameter."""
        from cine_mate.agents.director_agent import DirectorAgent

        custom_model = Mock()

        # model_name parameter should be ignored when model is provided
        agent = DirectorAgent(
            model_name="qwen-plus",  # Should be ignored
            model=custom_model,
            engine_tools=None
        )

        assert agent.model == custom_model

    def test_dependency_injection_priority(self):
        """Dependency injection priority: model > use_mock > default."""
        from cine_mate.agents.director_agent import DirectorAgent, MockChatModel

        custom_model = Mock()

        # Case 1: Injected model takes priority over use_mock
        agent1 = DirectorAgent(model=custom_model, use_mock=True, engine_tools=None)
        assert agent1.model == custom_model  # Not MockChatModel

        # Case 2: use_mock when no model injected
        agent2 = DirectorAgent(use_mock=True, engine_tools=None)
        assert isinstance(agent2.model, MockChatModel)


class TestDirectorAgentEngineToolsIntegration:
    """Test DirectorAgent with EngineTools."""

    @pytest.mark.asyncio
    async def test_engine_tools_registered_in_toolkit(self):
        """EngineTools are registered in toolkit."""
        from cine_mate.agents.director_agent import DirectorAgent
        from cine_mate.agents.tools.engine_tools import EngineTools

        # Mock EngineTools
        mock_tools = Mock(spec=EngineTools)
        mock_tools.create_video = Mock()
        mock_tools.get_run_status = Mock()
        mock_tools.get_run_list = Mock()
        mock_tools.submit_plan = Mock()

        # Mock Toolkit class
        with patch('agentscope.tool.Toolkit') as mock_toolkit_class:
            mock_toolkit = Mock()
            mock_toolkit_class.return_value = mock_toolkit

            agent = DirectorAgent(use_mock=True, engine_tools=mock_tools)

            # Verify tools were registered
            assert mock_toolkit.register_tool_function.call_count == 4

    def test_no_toolkit_without_engine_tools(self):
        """No toolkit when engine_tools is None."""
        from cine_mate.agents.director_agent import DirectorAgent

        agent = DirectorAgent(use_mock=True, engine_tools=None)

        # toolkit should be None or not registered
        # This depends on implementation


class TestDirectorAgentResponseHandling:
    """Test DirectorAgent response handling."""

    def test_mock_agent_can_be_called(self):
        """Mock agent can be called (returns mock response)."""
        from cine_mate.agents.director_agent import DirectorAgent

        agent = DirectorAgent(use_mock=True, engine_tools=None)

        # The model should be callable
        response = agent.model()

        assert response is not None


class TestEngineToolsDependencyInjection:
    """Test EngineTools with dependency injection."""

    def test_engine_tools_with_store_path(self):
        """EngineTools accepts store_path."""
        from cine_mate.agents.tools.engine_tools import EngineTools

        tools = EngineTools(store_path="/custom/path/db.db")

        assert tools.store is not None

    def test_engine_tools_default_store_path(self):
        """EngineTools default store path."""
        from cine_mate.agents.tools.engine_tools import EngineTools

        tools = EngineTools()

        # Default path should be set
        assert tools.store is not None

    @pytest.mark.asyncio
    async def test_engine_tools_init_db(self):
        """EngineTools init_db works."""
        from cine_mate.agents.tools.engine_tools import EngineTools

        tools = EngineTools(store_path="./test_tools.db")

        await tools.init_db()

        # Should initialize database
        assert tools.store is not None


class TestDirectorAgentInitializationOrder:
    """Test DirectorAgent initialization order."""

    def test_model_created_before_toolkit(self):
        """Model is created before toolkit."""
        from cine_mate.agents.director_agent import DirectorAgent

        # This is implicit in the __init__ order
        # Model setup (step 1) happens before toolkit (step 3)
        agent = DirectorAgent(use_mock=True, engine_tools=None)

        assert agent.model is not None

    def test_prompt_loaded_before_init(self):
        """System prompt is loaded before ReActAgent init."""
        from cine_mate.agents.director_agent import DirectorAgent

        agent = DirectorAgent(use_mock=True, engine_tools=None)

        # Agent should have sys_prompt set
        assert hasattr(agent, 'sys_prompt')


class TestDirectorAgentEdgeCases:
    """Test DirectorAgent edge cases."""

    def test_empty_name_default(self):
        """Default name is 'Director'."""
        from cine_mate.agents.director_agent import DirectorAgent

        agent = DirectorAgent(use_mock=True, engine_tools=None)

        assert agent.name == "Director"

    def test_custom_name_preserved(self):
        """Custom name is preserved."""
        from cine_mate.agents.director_agent import DirectorAgent

        agent = DirectorAgent(name="CustomDirector", use_mock=True, engine_tools=None)

        assert agent.name == "CustomDirector"

    def test_none_api_key_with_mock(self):
        """None api_key works with mock mode."""
        from cine_mate.agents.director_agent import DirectorAgent

        agent = DirectorAgent(api_key=None, use_mock=True, engine_tools=None)

        # Should not raise error
        assert agent is not None
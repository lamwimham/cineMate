"""
Tests for CineMate SkillLoader and Agent integration.
Covers on-demand loading, OpenCode format wrapping, and DirectorAgent skill injection.
"""

import pytest
import tempfile
from pathlib import Path

from cine_mate.skills.skill_store import SkillStore
from cine_mate.skills.skill_indexer import SkillIndexer
from cine_mate.skills.skill_loader import SkillLoader
from cine_mate.skills.models import SkillMetadata, SkillCategory
from cine_mate.agents.tools.skill_tool import make_load_skill_tool


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
async def skills_dir():
    """Provide a temporary skills directory."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
async def store(skills_dir):
    """Provide a fresh SkillStore instance."""
    s = SkillStore(skills_dir)
    await s.init()
    yield s


@pytest.fixture
async def populated_store(store):
    """SkillStore with pre-installed test skills."""
    await store.create(
        name="style-cyberpunk",
        content="""---
name: style-cyberpunk
description: Cyberpunk visual style with neon accents
category: style
version: 1.0.0
---

Cyberpunk style guide content with neon details.
""",
        metadata=SkillMetadata(
            name="style-cyberpunk",
            description="Cyberpunk visual style with neon accents",
            category=SkillCategory.STYLE,
            version="1.0.0",
        )
    )
    
    await store.create(
        name="workflow-short-ad",
        content="""---
name: workflow-short-ad
description: 15-second product ad template
category: workflow
version: 2.0.0
---

Workflow steps: hook -> demo -> CTA.
""",
        metadata=SkillMetadata(
            name="workflow-short-ad",
            description="15-second product ad template",
            category=SkillCategory.WORKFLOW,
            version="2.0.0",
        )
    )
    
    yield store


@pytest.fixture
def loader(populated_store):
    """Provide a SkillLoader backed by the populated store."""
    return SkillLoader(populated_store)


# =============================================================================
# SkillLoader Tests
# =============================================================================

class TestSkillLoaderLoad:
    """Test on-demand skill content loading."""
    
    @pytest.mark.asyncio
    async def test_load_returns_formatted_content(self, loader):
        """Load returns skill content wrapped in <skill_content> tags."""
        result = await loader.load("style-cyberpunk")
        
        assert result is not None
        assert '<skill_content' in result
        assert 'name="style-cyberpunk"' in result
        assert 'category="style"' in result
        assert 'version="1.0.0"' in result
        assert "Cyberpunk style guide content with neon details." in result
        assert "</skill_content>" in result
    
    @pytest.mark.asyncio
    async def test_load_missing_skill_returns_none(self, loader):
        """Load non-existent skill returns None."""
        result = await loader.load("nonexistent-skill")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_load_includes_metadata_in_tags(self, loader):
        """Load includes name, category, version in XML attributes."""
        result = await loader.load("workflow-short-ad")
        
        assert 'name="workflow-short-ad"' in result
        assert 'category="workflow"' in result
        assert 'version="2.0.0"' in result
        assert "Workflow steps: hook -> demo -> CTA." in result
    
    @pytest.mark.asyncio
    async def test_load_with_metadata_returns_dict(self, loader):
        """load_with_metadata returns structured dict."""
        result = await loader.load_with_metadata("style-cyberpunk")
        
        assert result is not None
        assert result["name"] == "style-cyberpunk"
        assert result["description"] == "Cyberpunk visual style with neon accents"
        assert result["category"] == "style"
        assert result["tags"] == []
        assert result["auto_generated"] is False
        assert "Cyberpunk style guide content with neon details." in result["content"]
    
    @pytest.mark.asyncio
    async def test_load_with_metadata_missing_returns_none(self, loader):
        """load_with_metadata returns None for missing skills."""
        result = await loader.load_with_metadata("nonexistent")
        assert result is None


# =============================================================================
# Skill Tool Tests
# =============================================================================

class TestSkillTool:
    """Test the load_skill() tool function for AgentScope."""
    
    @pytest.mark.asyncio
    async def test_tool_returns_content_for_valid_skill(self, populated_store):
        """Tool returns formatted content for existing skill."""
        loader = SkillLoader(populated_store)
        tool_fn = make_load_skill_tool(loader)
        
        response = await tool_fn("style-cyberpunk")
        
        assert response is not None
        text = response.content[0]["text"]
        assert '<skill_content' in text
        assert "Cyberpunk style guide content with neon details." in text
    
    @pytest.mark.asyncio
    async def test_tool_returns_error_for_missing_skill(self, populated_store):
        """Tool returns error message with available skills for missing skill."""
        loader = SkillLoader(populated_store)
        tool_fn = make_load_skill_tool(loader)
        
        response = await tool_fn("nonexistent-skill")
        
        text = response.content[0]["text"]
        assert "not found" in text
        assert "Available skills:" in text
        assert "style-cyberpunk" in text
        assert "workflow-short-ad" in text
    
    @pytest.mark.asyncio
    async def test_tool_has_correct_name(self, populated_store):
        """Tool function has correct name for AgentScope registration."""
        loader = SkillLoader(populated_store)
        tool_fn = make_load_skill_tool(loader)
        
        assert tool_fn.__name__ == "load_skill"
    
    @pytest.mark.asyncio
    async def test_tool_has_docstring(self, populated_store):
        """Tool function has docstring for schema generation."""
        loader = SkillLoader(populated_store)
        tool_fn = make_load_skill_tool(loader)
        
        assert tool_fn.__doc__ is not None
        assert "skill" in tool_fn.__doc__.lower()


# =============================================================================
# DirectorAgent Skill Integration Tests
# =============================================================================

class TestDirectorAgentSkillIntegration:
    """Test DirectorAgent skill system integration (mock mode)."""
    
    @pytest.mark.asyncio
    async def test_agent_accepts_skill_params(self, populated_store):
        """DirectorAgent accepts skill_indexer and skill_loader params."""
        from cine_mate.agents.director_agent import DirectorAgent
        from cine_mate.agents.tools.engine_tools import EngineTools
        
        store = SkillStore(Path(tempfile.mktemp(suffix=".db")))
        await store.init()
        
        indexer = SkillIndexer(store)
        loader = SkillLoader(store)
        tools = EngineTools(store_path=tempfile.mktemp(suffix=".db"))
        await tools.init_db()
        
        # Should not raise
        agent = DirectorAgent(
            name="Director",
            use_mock=True,
            engine_tools=tools,
            skill_indexer=indexer,
            skill_loader=loader,
        )
        
        assert agent is not None
        assert agent.name == "Director"
    
    @pytest.mark.asyncio
    async def test_agent_system_prompt_includes_skill_index(self, populated_store):
        """Agent system prompt includes skill index after inject_skills() call."""
        from cine_mate.agents.director_agent import DirectorAgent
        from cine_mate.agents.tools.engine_tools import EngineTools
        
        indexer = SkillIndexer(populated_store)
        loader = SkillLoader(populated_store)
        tools = EngineTools(store_path=tempfile.mktemp(suffix=".db"))
        await tools.init_db()
        
        agent = DirectorAgent(
            name="Director",
            use_mock=True,
            engine_tools=tools,
            skill_indexer=indexer,
            skill_loader=loader,
        )
        
        # Inject skills async (required when called from async context)
        await agent.inject_skills()
        
        # The sys_prompt should now contain the skill index
        sys_prompt = agent.sys_prompt
        assert "## Available Skills" in sys_prompt
        assert "style-cyberpunk" in sys_prompt
        assert "workflow-short-ad" in sys_prompt
    
    @pytest.mark.asyncio
    async def test_agent_without_skills_works_normally(self, populated_store):
        """Agent works without skill params (backward compatible)."""
        from cine_mate.agents.director_agent import DirectorAgent
        
        # Should not raise — skills are optional
        agent = DirectorAgent(
            name="Director",
            use_mock=True,
        )
        
        assert agent is not None
        assert agent.name == "Director"
        # No skill section in prompt
        assert "## Available Skills" not in agent.sys_prompt
    
    @pytest.mark.asyncio
    async def test_agent_with_only_indexer(self, populated_store):
        """Agent works with only skill_indexer (no loader)."""
        from cine_mate.agents.director_agent import DirectorAgent
        from cine_mate.agents.tools.engine_tools import EngineTools
        
        indexer = SkillIndexer(populated_store)
        tools = EngineTools(store_path=tempfile.mktemp(suffix=".db"))
        await tools.init_db()
        
        agent = DirectorAgent(
            name="Director",
            use_mock=True,
            engine_tools=tools,
            skill_indexer=indexer,
        )
        
        # Inject skills async
        await agent.inject_skills()
        
        assert agent is not None
        assert "## Available Skills" in agent.sys_prompt
    
    @pytest.mark.asyncio
    async def test_agent_with_only_loader(self, populated_store):
        """Agent works with only skill_loader (no indexer)."""
        from cine_mate.agents.director_agent import DirectorAgent
        from cine_mate.agents.tools.engine_tools import EngineTools
        
        loader = SkillLoader(populated_store)
        tools = EngineTools(store_path=tempfile.mktemp(suffix=".db"))
        await tools.init_db()
        
        agent = DirectorAgent(
            name="Director",
            use_mock=True,
            engine_tools=tools,
            skill_loader=loader,
        )
        
        assert agent is not None
        # No skill index in prompt (indexer not provided)
        assert "## Available Skills" not in agent.sys_prompt

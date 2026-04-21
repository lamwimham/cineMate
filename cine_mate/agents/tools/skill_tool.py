"""
CineMate Skill Tool for AgentScope Toolkit.

Provides the load_skill() tool function that the DirectorAgent can call
to retrieve full skill content on-demand (progressive disclosure pattern).

Registration:
    toolkit.register_tool_function(make_load_skill_tool(skill_loader))
"""

from typing import Optional

from agentscope.tool import ToolResponse

from cine_mate.skills.skill_loader import SkillLoader


def make_load_skill_tool(loader: SkillLoader):
    """
    Create an async load_skill tool function bound to a SkillLoader instance.
    
    The returned function can be registered with AgentScope Toolkit:
        toolkit.register_tool_function(make_load_skill_tool(loader))
    
    Args:
        loader: SkillLoader instance backing the tool
    
    Returns:
        Async function: load_skill(name: str) -> ToolResponse
    """
    
    async def load_skill(name: str) -> ToolResponse:
        """
        Load the full content of a skill by name.
        
        Use this when you need detailed guidance on style, workflow,
        or error recovery that isn't covered by the skill index alone.
        
        Args:
            name: Skill identifier (e.g., "style-cyberpunk", "workflow-short-ad")
        
        Returns:
            Full SKILL.md content wrapped in <skill_content> tags,
            or an error message if the skill is not found.
        """
        content = await loader.load(name)
        
        if content is None:
            available = await _list_available(loader)
            return ToolResponse(content=[{
                "type": "text",
                "text": f"Skill '{name}' not found.\n\nAvailable skills:\n{available}"
            }])
        
        return ToolResponse(content=[{"type": "text", "text": content}])
    
    # Attach docstring for AgentScope schema generation
    load_skill.__name__ = "load_skill"
    load_skill.__doc__ = """Load the full content of a skill by name. Use this when you need detailed guidance on style, workflow, or error recovery that isn't covered by the skill index alone. Args: name: Skill identifier (e.g., 'style-cyberpunk', 'workflow-short-ad'). Returns: Full SKILL.md content wrapped in <skill_content> tags, or an error message if the skill is not found."""
    
    return load_skill


async def _list_available(loader: SkillLoader) -> str:
    """List available skill names for error messages."""
    skills = await loader.store.list_all()
    if not skills:
        return "(No skills installed)"
    lines = [f"- {s.name}: {s.description}" for s in skills]
    return "\n".join(lines)

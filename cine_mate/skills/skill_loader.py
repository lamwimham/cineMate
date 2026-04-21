"""
CineMate SkillLoader — On-demand full skill content retrieval.

Wraps SkillStore to load complete SKILL.md content and return it in
the OpenCode progressive disclosure format:
    <skill_content name="...">
    ... full SKILL.md body ...
    </skill_content>

This pattern prevents context window overflow — the system prompt only
receives the skill index (name + description). Full content loads via
the load_skill() tool when the DirectorAgent decides it's relevant.
"""

from pathlib import Path
from typing import Optional

from cine_mate.skills.skill_store import SkillStore
from cine_mate.skills.models import SkillFullContent


class SkillLoader:
    """
    Loads full skill content on-demand for the DirectorAgent.
    
    Usage pattern (progressive disclosure):
    1. System prompt contains skill index (name + description only)
    2. DirectorAgent calls load_skill(name) when it needs details
    3. SkillLoader returns full SKILL.md wrapped in <skill_content> tags
    
    This follows the OpenCode pattern — compaction protects skill tool
    calls from pruning, ensuring the loaded content stays in context.
    """
    
    def __init__(self, store: SkillStore):
        self.store = store
    
    async def load(self, name: str) -> Optional[str]:
        """
        Load a skill's full content, wrapped in <skill_content> tags.
        
        Args:
            name: Skill identifier (e.g., "style-cyberpunk")
        
        Returns:
            Formatted string: <skill_content name="...">...body...</skill_content>
            or None if skill not found.
        """
        skill = await self.store.read(name)
        if skill is None:
            return None
        
        return self._format(skill)
    
    def _format(self, skill: SkillFullContent) -> str:
        """Wrap skill content in OpenCode-style XML tags."""
        meta = skill.metadata
        header = (
            f"<skill_content "
            f'name="{meta.name}" '
            f'category="{meta.category.value}" '
            f'version="{meta.version}">'
        )
        footer = "</skill_content>"
        
        return f"{header}\n{skill.content}\n{footer}"
    
    async def load_with_metadata(self, name: str) -> Optional[dict]:
        """
        Load skill content with metadata as a structured dict.
        
        Useful for programmatic access (e.g., SkillReviewer analysis).
        
        Returns:
            {
                "name": str,
                "description": str,
                "category": str,
                "tags": list,
                "auto_generated": bool,
                "content": str,
            }
            or None if not found.
        """
        skill = await self.store.read(name)
        if skill is None:
            return None
        
        meta = skill.metadata
        return {
            "name": meta.name,
            "description": meta.description,
            "category": meta.category.value,
            "tags": meta.tags,
            "auto_generated": meta.auto_generated,
            "source_run_id": meta.source_run_id,
            "content": skill.content,
        }

"""
CineMate SkillIndexer — Progressive Disclosure Index Builder

Scans the skills directory, builds an in-memory index, and provides
the `available()` method for the DirectorAgent's system prompt injection.

Progressive Disclosure Pattern (from OpenCode):
1. System prompt receives ONLY the skill index (name + description)
2. Full SKILL.md content loads on-demand via the skill() tool
3. This prevents context window overflow from loading all skills at once

Auto-Generation Support (from Hermes):
- Index includes `auto_generated` flag for provenance tracking
- Skills auto-created by SkillReviewer are indexed alongside hand-written ones
"""

import json
import aiosqlite
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from cine_mate.skills.models import (
    SkillMetadata, SkillCategory, SkillIndexEntry, SkillStatus
)
from cine_mate.skills.skill_store import SkillStore


class SkillIndexer:
    """
    Scans skill directory, builds and caches an index for progressive disclosure.
    
    The index is the lightweight view injected into the DirectorAgent's system prompt.
    Full content is loaded on-demand via SkillStore.read().
    """
    
    def __init__(self, store: SkillStore):
        self.store = store
        self._index: Optional[List[SkillIndexEntry]] = None
        self._last_scan: Optional[datetime] = None
    
    async def scan(self) -> List[SkillIndexEntry]:
        """
        Scan the skills directory and rebuild the index from SQLite metadata.
        
        Returns:
            List of SkillIndexEntry (lightweight, for system prompt injection)
        """
        all_skills = await self.store.list_all(status=SkillStatus.ENABLED)
        
        self._index = [
            SkillIndexEntry(
                name=skill.name,
                description=skill.description,
                category=skill.category,
                tags=skill.tags,
            )
            for skill in all_skills
        ]
        self._last_scan = datetime.now()
        return self._index
    
    async def available(
        self,
        agent: Optional[str] = None,
        scenario: Optional[str] = None,
        category: Optional[SkillCategory] = None,
    ) -> List[SkillIndexEntry]:
        """
        Return available skills, optionally filtered.
        
        This is the primary method called during system prompt construction.
        Returns only enabled skills matching the filter criteria.
        
        Args:
            agent: Filter by target agent (e.g., "director") — None = all
            scenario: Filter by trigger scenario — None = all
            category: Filter by skill category — None = all
        
        Returns:
            Filtered list of SkillIndexEntry for system prompt injection
        """
        # Lazy scan if not yet scanned
        if self._index is None:
            await self.scan()
        
        results = self._index
        
        if category:
            results = [s for s in results if s.category == category]
        
        # For agent/scenario filtering, need full metadata from SQLite
        if agent or scenario:
            all_meta = await self.store.list_all(status=SkillStatus.ENABLED)
            filtered_names = set()
            for skill in all_meta:
                if agent and skill.agent and skill.agent != agent:
                    continue
                if scenario and skill.scenario and skill.scenario != scenario:
                    continue
                filtered_names.add(skill.name)
            results = [s for s in results if s.name in filtered_names]
        
        return results
    
    def format_for_prompt(self, entries: Optional[List[SkillIndexEntry]] = None) -> str:
        """
        Format skill index for injection into DirectorAgent system prompt.
        
        Output format (OpenCode pattern):
        ## Available Skills
        - style-cyberpunk: Cyberpunk visual style with neon accents
        - workflow-short-ad: 15-second product ad template
        
        Args:
            entries: Skill entries to format (uses full index if None)
        """
        if entries is None:
            entries = self._index or []
        
        if not entries:
            return "## Available Skills\n(None available)"
        
        lines = ["## Available Skills"]
        for entry in entries:
            lines.append(entry.format_for_prompt())
        return "\n".join(lines)
    
    async def get_skill_names(self) -> List[str]:
        """Return list of all enabled skill names."""
        if self._index is None:
            await self.scan()
        return [s.name for s in self._index]
    
    def is_stale(self, max_age_seconds: float = 60.0) -> bool:
        """Check if the index needs rescanning."""
        if self._last_scan is None:
            return True
        return (datetime.now() - self._last_scan).total_seconds() > max_age_seconds
    
    async def refresh_if_stale(self, max_age_seconds: float = 60.0) -> List[SkillIndexEntry]:
        """Refresh the index if it's stale, otherwise return cached."""
        if self.is_stale(max_age_seconds):
            return await self.scan()
        return self._index or []

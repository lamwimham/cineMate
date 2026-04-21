"""
CineMate Skill System Data Models (Pydantic V2)
Skills provide progressive disclosure for the DirectorAgent — decision-layer
patterns (style strategies, workflow templates, error recovery), not
infrastructure code.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SkillCategory(str, Enum):
    STYLE = "style"              # Style strategy (e.g., cyberpunk, wong-kar-wai)
    WORKFLOW = "workflow"        # Workflow template (e.g., short-ad, product-review)
    ERROR_RECOVERY = "error"     # Error recovery patterns (e.g., kling-face-distortion)
    QUALITY = "quality"          # Quality gating and evaluation


class SkillStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class SkillMetadata(BaseModel):
    """
    Metadata extracted from SKILL.md YAML frontmatter.
    Mirrors the SQLite skills table schema.
    """
    name: str                    # Unique skill identifier (e.g., "style-cyberpunk")
    description: str             # Short description shown in progressive disclosure index
    category: SkillCategory
    version: str = "1.0.0"
    author: str = "cinemate"
    
    # Filtering
    agent: Optional[str] = None  # Target agent (e.g., "director", "editor") — None = all
    scenario: Optional[str] = None  # Trigger scenario (e.g., "video-generation", "style-transfer")
    tags: List[str] = Field(default_factory=list)
    
    # Provenance (for Hermes auto-generation mechanism)
    auto_generated: bool = False           # True if created by SkillReviewer
    source_run_id: Optional[str] = None    # Link to the PipelineRun that triggered this skill
    source_error: Optional[str] = None     # Error pattern that triggered auto-generation
    
    # Internal
    status: SkillStatus = SkillStatus.ENABLED
    content_hash: Optional[str] = None  # SHA256 of SKILL.md content for change detection
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class SkillIndexEntry(BaseModel):
    """
    Lightweight index entry for progressive disclosure.
    Only name + description injected into DirectorAgent system prompt.
    """
    name: str
    description: str
    category: SkillCategory
    tags: List[str] = Field(default_factory=list)
    
    def format_for_prompt(self) -> str:
        """Format as a single line for the available skills index."""
        tag_str = f" [{', '.join(self.tags)}]" if self.tags else ""
        return f"- {self.name}: {self.description}{tag_str}"


class SkillFullContent(BaseModel):
    """
    Complete skill content loaded on-demand via skill() tool.
    """
    metadata: SkillMetadata
    content: str  # Full SKILL.md markdown body (without frontmatter)

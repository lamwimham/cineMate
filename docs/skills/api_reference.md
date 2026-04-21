# CineMate Skill System — API Reference

> **Version**: Sprint 3 (v1.0.0)

---

## 📦 Module: `cine_mate.skills`

```python
from cine_mate.skills import (
    SkillMetadata,
    SkillIndexEntry,
    SkillFullContent,
    SkillCategory,
    SkillStatus,
    SkillStore,
    SkillIndexer,
    SkillLoader,
    SkillReviewer,
)
```

---

## 📊 Data Models

### SkillCategory

```python
class SkillCategory(str, Enum):
    STYLE = "style"              # Style strategy
    WORKFLOW = "workflow"        # Workflow template
    ERROR_RECOVERY = "error"     # Error recovery patterns
    QUALITY = "quality"          # Quality gating
```

### SkillStatus

```python
class SkillStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
```

### SkillMetadata

```python
class SkillMetadata(BaseModel):
    """Metadata extracted from SKILL.md YAML frontmatter."""
    
    name: str                    # Unique skill identifier
    description: str             # Short description (progressive disclosure)
    category: SkillCategory
    version: str = "1.0.0"
    author: str = "cinemate"
    
    # Filtering
    agent: Optional[str] = None  # Target agent (e.g., "director")
    scenario: Optional[str] = None  # Trigger scenario
    tags: List[str] = Field(default_factory=list)
    
    # Provenance (for Hermes auto-generation)
    auto_generated: bool = False
    source_run_id: Optional[str] = None
    source_error: Optional[str] = None
    
    # Internal
    status: SkillStatus = SkillStatus.ENABLED
    content_hash: Optional[str] = None  # SHA256 of SKILL.md
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

### SkillIndexEntry

```python
class SkillIndexEntry(BaseModel):
    """Lightweight index entry for progressive disclosure."""
    
    name: str
    description: str
    category: SkillCategory
    tags: List[str] = Field(default_factory=list)
    
    def format_for_prompt(self) -> str:
        """Format as a single line for the available skills index."""
        tag_str = f" [{', '.join(self.tags)}]" if self.tags else ""
        return f"- {self.name}: {self.description}{tag_str}"
```

### SkillFullContent

```python
class SkillFullContent(BaseModel):
    """Complete skill content loaded on-demand."""
    
    metadata: SkillMetadata
    content: str  # Full SKILL.md markdown body (without frontmatter)
```

---

## 🗄️ SkillStore

```python
class SkillStore:
    """
    SQLite + filesystem CRUD for skills.
    Provides persistent storage with change detection via SHA256.
    """
    
    def __init__(self, data_dir: Path):
        """Initialize with data directory path."""
        self.data_dir = data_dir
        self.db_path = data_dir / "skills.db"
    
    async def init(self) -> None:
        """Initialize SQLite database and sync with filesystem."""
    
    # ── CRUD Operations ─────────────────────────────────────────
    
    async def create(
        self,
        name: str,
        content: str,
        metadata: SkillMetadata,
    ) -> SkillMetadata:
        """
        Create a new skill.
        
        Args:
            name: Unique skill identifier
            content: Full SKILL.md content (without frontmatter)
            metadata: Skill metadata
        
        Returns:
            Created SkillMetadata with content_hash
        """
    
    async def read(self, name: str) -> Optional[SkillFullContent]:
        """
        Read full skill content by name.
        
        Args:
            name: Skill identifier
        
        Returns:
            SkillFullContent if found, None otherwise
        """
    
    async def update(
        self,
        name: str,
        content: Optional[str] = None,
        metadata: Optional[SkillMetadata] = None,
    ) -> Optional[SkillMetadata]:
        """
        Update skill content and/or metadata.
        
        Args:
            name: Skill identifier
            content: New content (optional)
            metadata: New metadata (optional)
        
        Returns:
            Updated SkillMetadata, None if not found
        """
    
    async def delete(self, name: str) -> bool:
        """
        Delete skill by name.
        
        Args:
            name: Skill identifier
        
        Returns:
            True if deleted, False if not found
        """
    
    # ── Query Operations ─────────────────────────────────────────
    
    async def list_all(self) -> List[SkillMetadata]:
        """List all skills metadata (no content)."""
    
    async def list_by_category(self, category: SkillCategory) -> List[SkillMetadata]:
        """List skills filtered by category."""
    
    async def list_by_tags(self, tags: List[str]) -> List[SkillMetadata]:
        """List skills matching any of the given tags."""
    
    async def search(self, query: str) -> List[SkillMetadata]:
        """Search skills by name or description."""
    
    # ── Sync Operations ─────────────────────────────────────────
    
    async def sync_from_fs(self) -> int:
        """
        Sync skills from filesystem SKILL.md files.
        Detects changes via SHA256 hash comparison.
        
        Returns:
            Number of skills synced/updated
        """
```

---

## 🔍 SkillIndexer

```python
class SkillIndexer:
    """
    Progressive disclosure index builder.
    Creates lightweight SkillIndexEntry for DirectorAgent system prompt.
    """
    
    def __init__(self, store: SkillStore):
        """Initialize with SkillStore instance."""
        self.store = store
    
    async def build_index(
        self,
        agent: Optional[str] = None,
        scenario: Optional[str] = None,
        category: Optional[SkillCategory] = None,
    ) -> List[SkillIndexEntry]:
        """
        Build progressive disclosure index.
        
        Args:
            agent: Filter by target agent
            scenario: Filter by trigger scenario
            category: Filter by category
        
        Returns:
            List of SkillIndexEntry (name + description only)
        """
    
    async def format_index_for_prompt(
        self,
        index: List[SkillIndexEntry],
    ) -> str:
        """
        Format index for DirectorAgent system prompt.
        
        Args:
            index: List of SkillIndexEntry
        
        Returns:
            Formatted string:
            "Available skills:
            - style-cyberpunk: Cyberpunk visual style [cyberpunk, neon]
            - workflow-short-ad: Short ad template [ad, product]"
        """
```

---

## 📂 SkillLoader

```python
class SkillLoader:
    """
    On-demand skill content loading.
    Returns full SKILL.md content when agent requests via skill() tool.
    """
    
    def __init__(self, store: SkillStore):
        """Initialize with SkillStore instance."""
        self.store = store
    
    async def load(self, name: str) -> Optional[str]:
        """
        Load full skill content by name.
        
        Args:
            name: Skill identifier
        
        Returns:
            Full SKILL.md content formatted as OpenCode XML:
            <skill_content name="style-cyberpunk">
            ## Overview
            ...
            </skill_content>
        """
```

---

## 🤖 SkillReviewer

```python
class SkillReviewer:
    """
    Hermes auto-generation mechanism.
    Analyzes PipelineRun execution and creates skills from patterns.
    """
    
    def __init__(self, store: SkillStore):
        """Initialize with SkillStore instance."""
        self.store = store
    
    async def review(self, run_data: Dict[str, Any]) -> Optional[SkillMetadata]:
        """
        Review a completed PipelineRun and potentially create a skill.
        
        Args:
            run_data: PipelineRun execution data:
                - run_id: str
                - status: "completed" | "failed" | "retried"
                - intent: str (original user prompt)
                - nodes: list of node execution records
                - error: optional error info (for failed runs)
                - retry_count: int
        
        Returns:
            SkillMetadata if skill created, None otherwise
        
        Review Triggers:
            - Success (3+ nodes): Creates WORKFLOW skill
            - Failure (identifiable error): Creates ERROR_RECOVERY skill
            - Retry (2+): Creates ERROR_RECOVERY skill
        
        Skip Conditions:
            - <3 nodes (too simple)
            - Generic errors (timeout/cancelled/user_interrupt)
            - Already reviewed (dedup by source_run_id)
            - Single retry (too common)
        """
```

---

## 🔧 Integration with DirectorAgent

### Skill Tool Factory

```python
from cine_mate.agents.tools.skill_tool import make_load_skill_tool

# Create skill tool for DirectorAgent
load_skill_tool = make_load_skill_tool(skill_loader)

# DirectorAgent can now call skill tool
agent = DirectorAgent(
    name="Director",
    model_config={"model_type": "openai", "model_name": "gpt-4"},
    tools=[load_skill_tool],
)
```

### Async Integration

```python
from cine_mate.agents.director_agent import DirectorAgent

async def setup_agent():
    store = SkillStore(Path("./cine_mate/skills/data"))
    await store.init()
    
    # Inject skill index into agent
    agent = DirectorAgent(...)
    await agent.inject_skills()  # Async skill injection
    
    # Agent now has skill index in system prompt
```

---

## 📋 Example Usage

### Create a Style Skill

```python
from cine_mate.skills import SkillStore, SkillMetadata, SkillCategory
from pathlib import Path

async def create_skill():
    store = SkillStore(Path("./cine_mate/skills/data"))
    await store.init()
    
    metadata = SkillMetadata(
        name="style-wong-kar-wai",
        description="Wong Kar-wai cinematography style",
        category=SkillCategory.STYLE,
        tags=["wong-kar-wai", "cinematography", "step-printing"],
    )
    
    content = """
# Wong Kar-wai Visual Style

## Overview
Step-printing, slow motion, handheld camera...

## Color Palette
Warm tones, saturated colors...
"""
    
    await store.create(
        name="style-wong-kar-wai",
        content=content,
        metadata=metadata,
    )
```

### Build Progressive Disclosure Index

```python
from cine_mate.skills import SkillIndexer

async def build_index():
    indexer = SkillIndexer(store)
    
    # Build index for director agent
    index = await indexer.build_index(agent="director")
    
    # Format for prompt injection
    prompt_text = await indexer.format_index_for_prompt(index)
    
    print(prompt_text)
    # Output:
    # Available skills:
    # - style-cyberpunk: Cyberpunk visual style [cyberpunk, neon]
    # - workflow-short-ad: Short ad template [ad, product]
```

### Auto-Generate from PipelineRun

```python
from cine_mate.skills import SkillReviewer

async def review_run():
    reviewer = SkillReviewer(store)
    
    # Simulate a successful run
    run_data = {
        "run_id": "run_001",
        "status": "completed",
        "intent": "Create a product ad video",
        "nodes": [
            {"id": "script", "type": "script_gen", "status": "succeeded"},
            {"id": "image", "type": "text_to_image", "status": "succeeded"},
            {"id": "video", "type": "image_to_video", "status": "succeeded"},
        ],
        "retry_count": 0,
    }
    
    result = await reviewer.review(run_data)
    
    if result:
        print(f"Auto-generated skill: {result.name}")
        print(f"Category: {result.category}")
        print(f"Source: {result.source_run_id}")
```

---

## 🧪 Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| SkillStore | 29 | 95% |
| SkillLoader | 14 | 92% |
| SkillReviewer | 15 | 93% |
| **Total** | **58** | **93%** |

---

## 🔗 Related Documentation

- [User Guide](user_guide.md)
- [Architecture Overview](../architecture.md)
- [Director Agent Integration](../agentscope_guide.md)

---

<p align="center">
  <strong>CineMate Skill System API</strong> — Progressive disclosure + Auto-generation
</p>
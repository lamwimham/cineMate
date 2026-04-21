"""
Tests for CineMate SkillStore and SkillIndexer.
Covers CRUD operations, frontmatter validation, progressive disclosure indexing,
and auto-generation provenance tracking.
"""

import pytest
import tempfile
from pathlib import Path

from cine_mate.skills.skill_store import SkillStore
from cine_mate.skills.skill_indexer import SkillIndexer
from cine_mate.skills.models import (
    SkillMetadata, SkillCategory, SkillStatus, SkillIndexEntry
)


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
async def indexer(store):
    """Provide a SkillIndexer backed by the store."""
    return SkillIndexer(store)


@pytest.fixture
async def populated_store(store):
    """SkillStore with pre-installed test skills."""
    await store.create(
        name="style-cyberpunk",
        content="""---
name: style-cyberpunk
description: Cyberpunk visual style with neon accents
category: style
tags: [neon, sci-fi]
---

Cyberpunk style guide content here.
""",
        metadata=SkillMetadata(
            name="style-cyberpunk",
            description="Cyberpunk visual style with neon accents",
            category=SkillCategory.STYLE,
            tags=["neon", "sci-fi"],
            scenario="style-transfer",
        )
    )
    
    await store.create(
        name="workflow-short-ad",
        content="""---
name: workflow-short-ad
description: 15-second product ad template
category: workflow
tags: [advertising]
---

Short ad workflow content here.
""",
        metadata=SkillMetadata(
            name="workflow-short-ad",
            description="15-second product ad template",
            category=SkillCategory.WORKFLOW,
            tags=["advertising"],
            scenario="product-video",
            agent="director",
        )
    )
    
    await store.create(
        name="error-kling-faces",
        content="""---
name: error-kling-faces
description: Recovery pattern for Kling face distortion
category: error
auto_generated: true
source_run_id: run_042
source_error: "face_distortion_v2"
---

Error recovery pattern for face distortion.
""",
        metadata=SkillMetadata(
            name="error-kling-faces",
            description="Recovery pattern for Kling face distortion",
            category=SkillCategory.ERROR_RECOVERY,
            auto_generated=True,
            source_run_id="run_042",
            source_error="face_distortion_v2",
        )
    )
    
    yield store


# =============================================================================
# SkillStore Tests
# =============================================================================

class TestSkillStoreCreate:
    """Test skill creation with frontmatter and metadata."""
    
    @pytest.mark.asyncio
    async def test_create_with_frontmatter(self, store):
        """Create skill from content with YAML frontmatter."""
        content = """---
name: style-retro
description: Retro 80s visual style
category: style
version: 2.0.0
---

Retro style guide content.
"""
        meta = await store.create("style-retro", content)
        
        assert meta.name == "style-retro"
        assert meta.description == "Retro 80s visual style"
        assert meta.category == SkillCategory.STYLE
        assert meta.version == "2.0.0"
        assert meta.content_hash is not None
    
    @pytest.mark.asyncio
    async def test_create_with_metadata_override(self, store):
        """Create skill with explicit metadata override."""
        meta = await store.create(
            name="style-minimal",
            content="Minimal style content.",
            metadata=SkillMetadata(
                name="style-minimal",
                description="Minimal clean style",
                category=SkillCategory.STYLE,
                tags=["clean", "minimal"],
            )
        )
        
        assert meta.description == "Minimal clean style"
        assert meta.tags == ["clean", "minimal"]
    
    @pytest.mark.asyncio
    async def test_create_writes_filesystem(self, store):
        """Create skill writes SKILL.md to data directory."""
        await store.create(
            name="test-skill",
            content="Test content.",
            metadata=SkillMetadata(
                name="test-skill",
                description="Test",
                category=SkillCategory.STYLE,
            )
        )
        
        skill_file = store._skill_file("test-skill")
        assert skill_file.exists()
        content = skill_file.read_text()
        assert "---" in content  # Has frontmatter
        assert "Test content." in content
    
    @pytest.mark.asyncio
    async def test_create_writes_sqlite(self, store):
        """Create skill writes metadata to SQLite."""
        meta = await store.create(
            name="test-skill",
            content="Test content.",
            metadata=SkillMetadata(
                name="test-skill",
                description="Test",
                category=SkillCategory.STYLE,
            )
        )
        
        skills = await store.list_all()
        assert any(s.name == "test-skill" for s in skills)
    
    @pytest.mark.asyncio
    async def test_create_auto_generated_provenance(self, store):
        """Create skill with auto-generation metadata (Hermes pattern)."""
        meta = await store.create(
            name="error-auto-recovered",
            content="Auto-generated error recovery.",
            metadata=SkillMetadata(
                name="error-auto-recovered",
                description="Auto-recovered error pattern",
                category=SkillCategory.ERROR_RECOVERY,
                auto_generated=True,
                source_run_id="run_099",
                source_error="timeout_kling_v1",
            )
        )
        
        assert meta.auto_generated is True
        assert meta.source_run_id == "run_099"
        assert meta.source_error == "timeout_kling_v1"
    
    @pytest.mark.asyncio
    async def test_create_computes_content_hash(self, store):
        """Create skill computes SHA256 hash for change detection."""
        meta = await store.create(
            name="hash-test",
            content="Original content.",
            metadata=SkillMetadata(
                name="hash-test",
                description="Hash test",
                category=SkillCategory.STYLE,
            )
        )
        
        assert meta.content_hash is not None
        assert len(meta.content_hash) == 16  # Truncated SHA256
        
        # Update content, hash should change
        await store.update("hash-test", "Modified content.")
        updated = await store.read("hash-test")
        assert updated.metadata.content_hash != meta.content_hash


class TestSkillStoreRead:
    """Test skill reading with progressive disclosure."""
    
    @pytest.mark.asyncio
    async def test_read_returns_full_content(self, populated_store):
        """Read skill returns SkillFullContent with metadata + body."""
        result = await populated_store.read("style-cyberpunk")
        
        assert result is not None
        assert result.metadata.name == "style-cyberpunk"
        assert "Cyberpunk style guide content here." in result.content
    
    @pytest.mark.asyncio
    async def test_read_missing_skill_returns_none(self, store):
        """Read non-existent skill returns None."""
        result = await store.read("nonexistent-skill")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_read_auto_generated_skill(self, populated_store):
        """Read auto-generated skill preserves provenance."""
        result = await populated_store.read("error-kling-faces")
        
        assert result.metadata.auto_generated is True
        assert result.metadata.source_run_id == "run_042"
        assert result.metadata.source_error == "face_distortion_v2"


class TestSkillStoreUpdate:
    """Test skill updates."""
    
    @pytest.mark.asyncio
    async def test_update_existing_skill(self, populated_store):
        """Update modifies content and metadata."""
        result = await populated_store.update(
            "style-cyberpunk",
            """---
name: style-cyberpunk
description: Updated cyberpunk description
category: style
---

Updated content body.
"""
        )
        
        assert result is not None
        assert result.description == "Updated cyberpunk description"
        
        # Verify filesystem updated
        full = await populated_store.read("style-cyberpunk")
        assert "Updated content body." in full.content
    
    @pytest.mark.asyncio
    async def test_update_missing_skill_returns_none(self, store):
        """Update non-existent skill returns None."""
        result = await store.update("nonexistent", "new content")
        assert result is None


class TestSkillStoreDelete:
    """Test skill deletion."""
    
    @pytest.mark.asyncio
    async def test_delete_existing_skill(self, populated_store):
        """Delete removes filesystem + SQLite."""
        result = await populated_store.delete("style-cyberpunk")
        assert result is True
        
        # Filesystem removed
        assert not populated_store._skill_file("style-cyberpunk").exists()
        
        # SQLite removed
        skills = await populated_store.list_all()
        assert not any(s.name == "style-cyberpunk" for s in skills)
    
    @pytest.mark.asyncio
    async def test_delete_missing_skill_returns_false(self, store):
        """Delete non-existent skill returns False."""
        result = await store.delete("nonexistent")
        assert result is False


class TestSkillStoreList:
    """Test skill listing and filtering."""
    
    @pytest.mark.asyncio
    async def test_list_all_skills(self, populated_store):
        """List returns all enabled skills."""
        skills = await populated_store.list_all()
        assert len(skills) == 3
    
    @pytest.mark.asyncio
    async def test_list_filter_by_status(self, store):
        """List can filter by status."""
        await store.create(
            name="active-skill",
            content="Active.",
            metadata=SkillMetadata(
                name="active-skill",
                description="Active",
                category=SkillCategory.STYLE,
                status=SkillStatus.ENABLED,
            )
        )
        
        enabled = await store.list_all(status=SkillStatus.ENABLED)
        assert len(enabled) == 1
        assert enabled[0].name == "active-skill"
    
    @pytest.mark.asyncio
    async def test_exists(self, populated_store):
        """Exists check works correctly."""
        assert await populated_store.exists("style-cyberpunk") is True
        assert await populated_store.exists("nonexistent") is False


# =============================================================================
# SkillIndexer Tests
# =============================================================================

class TestSkillIndexerScan:
    """Test index building and caching."""
    
    @pytest.mark.asyncio
    async def test_scan_builds_index(self, populated_store, indexer):
        """Scan reads all enabled skills and builds index."""
        entries = await indexer.scan()
        
        assert len(entries) == 3
        names = {e.name for e in entries}
        assert "style-cyberpunk" in names
        assert "workflow-short-ad" in names
        assert "error-kling-faces" in names
    
    @pytest.mark.asyncio
    async def test_scan_excludes_disabled(self, store, indexer):
        """Scan only includes enabled skills."""
        await store.create(
            name="disabled-skill",
            content="Disabled.",
            metadata=SkillMetadata(
                name="disabled-skill",
                description="A disabled skill",
                category=SkillCategory.STYLE,
                status=SkillStatus.DISABLED,
            )
        )
        
        entries = await indexer.scan()
        assert not any(e.name == "disabled-skill" for e in entries)


class TestSkillIndexerAvailable:
    """Test progressive disclosure filtering."""
    
    @pytest.mark.asyncio
    async def test_available_all(self, populated_store, indexer):
        """Available() returns all enabled skills when no filters."""
        await indexer.scan()
        entries = await indexer.available()
        assert len(entries) == 3
    
    @pytest.mark.asyncio
    async def test_available_filter_by_category(self, populated_store, indexer):
        """Available() filters by category."""
        await indexer.scan()
        entries = await indexer.available(category=SkillCategory.STYLE)
        assert len(entries) == 1
        assert entries[0].name == "style-cyberpunk"
    
    @pytest.mark.asyncio
    async def test_available_filter_by_scenario(self, populated_store, indexer):
        """Available() filters by scenario; None = universal (included)."""
        await indexer.scan()
        # workflow-short-ad has scenario="product-video" (matches)
        # error-kling-faces has scenario=None (universal, included)
        # style-cyberpunk has scenario="style-transfer" (excluded)
        entries = await indexer.available(scenario="product-video")
        assert len(entries) == 2
        names = {e.name for e in entries}
        assert "workflow-short-ad" in names
        assert "error-kling-faces" in names
    
    @pytest.mark.asyncio
    async def test_available_filter_by_agent(self, populated_store, indexer):
        """Available() filters by agent; None = universal (included)."""
        await indexer.scan()
        # workflow-short-ad has agent="director" (matches)
        # style-cyberpunk and error-kling-faces have agent=None (universal)
        entries = await indexer.available(agent="director")
        assert len(entries) == 3  # All skills are available to director
        names = {e.name for e in entries}
        assert "workflow-short-ad" in names
    
    @pytest.mark.asyncio
    async def test_available_exclusive_agent_filter(self, store, indexer):
        """Skills with a specific agent constraint are excluded when filtering for another agent."""
        # Create a skill only for "editor" agent
        await store.create(
            name="editor-only",
            content="Editor skill.",
            metadata=SkillMetadata(
                name="editor-only",
                description="Editor-only skill",
                category=SkillCategory.STYLE,
                agent="editor",
            )
        )
        # Create a universal skill
        await store.create(
            name="universal",
            content="Universal skill.",
            metadata=SkillMetadata(
                name="universal",
                description="Universal skill",
                category=SkillCategory.STYLE,
            )
        )
        
        await indexer.scan()
        entries = await indexer.available(agent="director")
        names = {e.name for e in entries}
        assert "universal" in names  # Universal skills included
        assert "editor-only" not in names  # Editor-only skill excluded


class TestSkillIndexerPromptFormat:
    """Test system prompt injection formatting."""
    
    @pytest.mark.asyncio
    async def test_format_for_prompt(self, populated_store, indexer):
        """Format produces OpenCode-style skill index."""
        await indexer.scan()
        entries = await indexer.available()
        formatted = indexer.format_for_prompt(entries)
        
        assert "## Available Skills" in formatted
        assert "- style-cyberpunk:" in formatted
        assert "- workflow-short-ad:" in formatted
        assert "- error-kling-faces:" in formatted
    
    @pytest.mark.asyncio
    async def test_format_empty(self, indexer):
        """Format handles empty index gracefully."""
        formatted = indexer.format_for_prompt([])
        assert "(None available)" in formatted


class TestSkillIndexerCaching:
    """Test index caching and staleness."""
    
    @pytest.mark.asyncio
    async def test_is_stale_initial(self, indexer):
        """Index is stale before first scan."""
        assert indexer.is_stale() is True
    
    @pytest.mark.asyncio
    async def test_is_stale_after_scan(self, indexer):
        """Index is fresh immediately after scan."""
        await indexer.scan()
        assert indexer.is_stale() is False
    
    @pytest.mark.asyncio
    async def test_refresh_if_stale(self, populated_store, indexer):
        """Refresh rescans when stale, returns cached when fresh."""
        # First call triggers scan
        entries = await indexer.refresh_if_stale()
        assert len(entries) == 3
        
        # Second call returns cached
        entries2 = await indexer.refresh_if_stale()
        assert entries2 is entries  # Same object (cached)
    
    @pytest.mark.asyncio
    async def test_get_skill_names(self, populated_store, indexer):
        """Get skill names returns list of strings."""
        names = await indexer.get_skill_names()
        assert isinstance(names, list)
        assert all(isinstance(n, str) for n in names)
        assert len(names) == 3

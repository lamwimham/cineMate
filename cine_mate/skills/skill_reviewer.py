"""
CineMate SkillReviewer — Auto-generation of skills from PipelineRun analysis.

Implements the Hermes auto-generation mechanism:
- Analyzes PipelineRun execution logs and outcomes
- Identifies reusable patterns (successful workflows, error recovery)
- Creates new skills with provenance tracking (source_run_id, source_error)
- Triggered by Orchestrator on pipeline completion (success/failure/retry)

This is the self-improving component of the Skill System — the agent
learns from experience and persists that knowledge as skills.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from cine_mate.skills.skill_store import SkillStore
from cine_mate.skills.models import SkillMetadata, SkillCategory


class SkillReviewer:
    """
    Analyzes PipelineRun outcomes and auto-generates skills.
    
    Triggers:
    - PipelineRun completion (success)
    - PipelineRun failure with identifiable error patterns
    - PipelineRun with retries (error recovery patterns)
    
    Output:
    - New skills created via SkillStore with provenance metadata
    - Skills marked as auto_generated=True for auditability
    """
    
    def __init__(self, store: SkillStore):
        self.store = store
    
    async def review(self, run_data: Dict[str, Any]) -> Optional[SkillMetadata]:
        """
        Review a completed PipelineRun and potentially create a skill.
        
        Args:
            run_data: PipelineRun execution data containing:
                - run_id: str
                - status: "completed" | "failed" | "retried"
                - intent: str (original user prompt intent)
                - nodes: list of node execution records
                - error: optional error info (for failed runs)
                - retry_count: int (number of retries)
        
        Returns:
            SkillMetadata if a skill was created, None otherwise.
        """
        status = run_data.get("status", "")
        nodes = run_data.get("nodes", [])
        intent = run_data.get("intent", "")
        run_id = run_data.get("run_id", "")
        error = run_data.get("error")
        retry_count = run_data.get("retry_count", 0)
        
        # Determine review outcome
        if status == "completed":
            return await self._review_success(run_id, intent, nodes)
        elif status == "failed" and error:
            return await self._review_failure(run_id, intent, nodes, error)
        elif status == "retried" and retry_count > 0:
            return await self._review_retry(run_id, intent, nodes, retry_count)
        
        return None
    
    async def _review_success(
        self, run_id: str, intent: str, nodes: List[Dict]
    ) -> Optional[SkillMetadata]:
        """
        Review a successful run — look for reusable workflow patterns.
        
        Creates a workflow skill if the run used a non-trivial node pattern
        (3+ nodes) that could serve as a template.
        """
        if len(nodes) < 3:
            return None  # Too simple to be a reusable pattern
        
        # Extract node type sequence
        node_sequence = [n.get("type", "") for n in nodes if n.get("type")]
        
        # Skip if we already have a very similar workflow
        existing_skills = await self.store.list_all()
        for skill in existing_skills:
            if skill.auto_generated and skill.source_run_id == run_id:
                return None  # Already reviewed this run
        
        # Generate skill from successful workflow
        skill_name = f"workflow-auto-{run_id}"
        description = f"Auto-generated from successful run: {intent[:50]}..."
        
        # Build skill content from execution data
        content = self._build_workflow_content(intent, nodes, node_sequence)
        
        metadata = await self.store.create(
            name=skill_name,
            content=content,
            metadata=SkillMetadata(
                name=skill_name,
                description=description,
                category=SkillCategory.WORKFLOW,
                auto_generated=True,
                source_run_id=run_id,
                tags=["auto-generated", "workflow"],
            )
        )
        
        return metadata
    
    async def _review_failure(
        self, run_id: str, intent: str, nodes: List[Dict], error: Dict
    ) -> Optional[SkillMetadata]:
        """
        Review a failed run — look for identifiable error patterns
        that could become error recovery skills.
        """
        error_msg = error.get("message", "")
        error_type = error.get("type", "unknown")
        
        # Skip generic errors
        generic_errors = ["timeout", "cancelled", "user_interrupt"]
        if any(g in error_type.lower() for g in generic_errors):
            return None
        
        # Identify the failing node
        failing_node = None
        for node in nodes:
            if node.get("status") == "failed":
                failing_node = node
                break
        
        if not failing_node:
            return None
        
        node_type = failing_node.get("type", "unknown")
        
        # Generate error recovery skill
        skill_name = f"error-{node_type}-{error_type.lower().replace(' ', '-')[:20]}"
        description = f"Recovery pattern for {node_type} error: {error_msg[:60]}..."
        
        content = self._build_error_content(node_type, error_msg, error_type, failing_node)
        
        metadata = await self.store.create(
            name=skill_name,
            content=content,
            metadata=SkillMetadata(
                name=skill_name,
                description=description,
                category=SkillCategory.ERROR_RECOVERY,
                auto_generated=True,
                source_run_id=run_id,
                source_error=error_type,
                tags=["auto-generated", "error-recovery", node_type],
            )
        )
        
        return metadata
    
    async def _review_retry(
        self, run_id: str, intent: str, nodes: List[Dict], retry_count: int
    ) -> Optional[SkillMetadata]:
        """
        Review a retried run — capture the recovery pattern that
        eventually succeeded after retries.
        """
        if retry_count < 2:
            return None  # Single retry is too common to patternize
        
        # Find the node that required retries
        retried_nodes = [n for n in nodes if n.get("retry_count", 0) > 0]
        if not retried_nodes:
            return None
        
        node = retried_nodes[0]
        node_type = node.get("type", "unknown")
        
        skill_name = f"recovery-{node_type}-retry-{retry_count}"
        description = f"Retry recovery for {node_type} ({retry_count} retries)"
        
        content = self._build_recovery_content(node_type, retry_count, node)
        
        metadata = await self.store.create(
            name=skill_name,
            content=content,
            metadata=SkillMetadata(
                name=skill_name,
                description=description,
                category=SkillCategory.ERROR_RECOVERY,
                auto_generated=True,
                source_run_id=run_id,
                source_error=f"retry_{retry_count}",
                tags=["auto-generated", "retry-recovery", node_type],
            )
        )
        
        return metadata
    
    # --- Content Builders ---
    
    def _build_workflow_content(
        self, intent: str, nodes: List[Dict], node_sequence: List[str]
    ) -> str:
        """Build workflow skill content from successful execution."""
        lines = [
            f"# Auto-Generated Workflow: {intent[:50]}",
            "",
            "## Node Sequence",
            "",
        ]
        for i, node_type in enumerate(node_sequence):
            lines.append(f"{i+1}. `{node_type}`")
        
        lines.extend([
            "",
            "## Configuration",
            "",
            "```json",
            json.dumps({
                "nodes": [
                    {"id": n.get("id", ""), "type": n.get("type", ""), "params": n.get("params", {})}
                    for n in nodes
                ]
            }, indent=2, ensure_ascii=False),
            "```",
            "",
            "## Notes",
            "",
            f"- Auto-generated from run execution",
            f"- Total nodes: {len(nodes)}",
            f"- Original intent: {intent}",
        ])
        return "\n".join(lines)
    
    def _build_error_content(
        self, node_type: str, error_msg: str, error_type: str, node: Dict
    ) -> str:
        """Build error recovery skill content."""
        return f"""# Error Recovery: {node_type} — {error_type}

## Error Pattern
- **Node Type**: `{node_type}`
- **Error Type**: {error_type}
- **Message**: {error_msg}

## Recommended Recovery
1. Check input parameters for {node_type}
2. Verify API key/credentials
3. Retry with reduced parameters (lower resolution, shorter duration)
4. If persistent, switch to fallback provider

## Configuration at Failure
```json
{json.dumps(node.get("params", {}), indent=2, ensure_ascii=False)}
```
"""
    
    def _build_recovery_content(
        self, node_type: str, retry_count: int, node: Dict
    ) -> str:
        """Build retry recovery skill content."""
        return f"""# Retry Recovery: {node_type} ({retry_count} retries)

## Pattern
- **Node Type**: `{node_type}`
- **Retries Before Success**: {retry_count}
- **Node ID**: {node.get("id", "unknown")}

## Recovery Steps
1. First attempt failed — check error logs
2. Retry with same parameters (transient error)
3. If retry fails, reduce complexity (resolution/duration)
4. If still failing, switch to fallback provider

## Configuration
```json
{json.dumps(node.get("params", {}), indent=2, ensure_ascii=False)}
```
"""

# [Feature] Human-in-the-Loop (HITL) Support for Node Approval

> **Status**: Backlog  
> **Priority**: P2 (Sprint 3+)  
> **Labels**: `enhancement`, `fsm`, `approval`, `ux`  
> **Assignees**: TBD (hermes/copaw)  

---

## 🎯 Summary

Implement **Human-in-the-Loop (HITL)** capability allowing human operators to review and approve/reject individual node executions before they proceed. This is critical for high-stakes production workflows where creative control and quality assurance are paramount.

**Key Insight**: Architecture already supports HITL at the FSM level (`QUALITY_CHECK` → `APPROVAL` states), but Orchestrator lacks the pause-and-wait mechanism.

---

## 🎬 User Stories

### Story 1: Creative Director Review
> As a **Creative Director**, I want to review AI-generated video clips before they are used in downstream compositing, so that I can ensure the creative vision is maintained.

**Scenario**: Director Agent generates 5 scene variations → Human selects best 3 → Only selected scenes proceed to final render.

### Story 2: Quality Assurance Checkpoint
> As a **QA Lead**, I want to inspect outputs from the image generation node before they are passed to video generation, so that I can catch artifacts early and avoid wasted compute.

**Scenario**: Image generation completes → QA reviews 10 images → Approves 8, rejects 2 with feedback → Rejected nodes retry with adjusted prompts.

### Story 3: Client Approval Workflow
> As a **Producer**, I want to send preview links to external clients and wait for their approval before finalizing high-cost renders.

**Scenario**: Rough cut generated → Client receives email with preview → Client approves via web UI → Final 4K render proceeds.

---

## 🏗️ Architecture Overview

### Current State (Simplified)

```
┌─────────┐      ┌─────────────┐      ┌──────────┐
│ EXECUTE │ ───> │ QUALITY_CHK │ ───> │ SUCCEED  │
└─────────┘      └─────────────┘      └──────────┘
                      ↓
                   [AUTO PASS]
```

### Target State (With HITL)

```
┌─────────┐      ┌─────────────┐      ┌──────────┐      ┌──────────┐
│ EXECUTE │ ───> │ QUALITY_CHK │ ───> │ APPROVAL │ ───> │ SUCCEED  │
└─────────┘      └─────────────┘      └──────────┘      └──────────┘
                      ↓                     ↓
                 [AI CHECK]           [HUMAN REVIEW]
                 (auto pass)          (approve/reject)
                                          ↓
                                     ┌──────────┐
                                     │  RETRY   │
                                     └──────────┘
```

---

## 🔧 Technical Design

### Option A: Synchronous Blocking (Simple)

```python
# cine_mate/engine/orchestrator.py

async def _execute_node(self, node_id: str):
    # ... execution ...
    
    fsm.transition("complete")  # -> QUALITY_CHECK
    
    # Check if human approval required
    if node_config.get("requires_human_approval", False):
        fsm.transition("review")  # -> APPROVAL
        
        # PAUSE: Wait for human input
        approval_result = await self._wait_for_human_approval(
            run_id=self.run.run_id,
            node_id=node_id,
            artifact=result,
            timeout=node_config.get("approval_timeout", 3600)  # 1 hour default
        )
        
        if approval_result.decision == "approve":
            fsm.transition("approve")
            # Add human feedback to trace
            await self._log_human_feedback(
                run_id=self.run.run_id,
                node_id=node_id,
                feedback=approval_result.feedback
            )
        else:
            fsm.transition("reject")
            raise HumanRejectedError(approval_result.feedback)
    else:
        fsm.transition("pass")  # Auto-approve

async def _wait_for_human_approval(
    self, 
    run_id: str, 
    node_id: str, 
    artifact: Artifact,
    timeout: int
) -> ApprovalResult:
    """
    Block until human provides approval decision.
    
    Implementation options:
    1. Poll database for approval record
    2. Use asyncio.Event with webhook trigger
    3. Use Redis pub/sub with timeout
    """
    # Placeholder: Actual implementation depends on UI layer
    pass
```

**Pros**: Simple, deterministic  
**Cons**: Blocks worker, requires long-running process

---

### Option B: Asynchronous Event-Driven (Recommended)

```python
# cine_mate/engine/orchestrator.py

async def _execute_node(self, node_id: str):
    # ... execution ...
    
    fsm.transition("complete")  # -> QUALITY_CHECK
    
    if node_config.get("requires_human_approval", False):
        fsm.transition("review")  # -> APPROVAL
        
        # Publish approval request event (NON-BLOCKING)
        await self.event_bus.publish(
            channel="approval_required",
            event=ApprovalRequiredEvent(
                run_id=self.run.run_id,
                node_id=node_id,
                preview_url=artifact.preview_url,
                created_at=datetime.now(),
                timeout_seconds=3600
            )
        )
        
        # Store checkpoint for recovery
        await self.store.save_execution_checkpoint(
            run_id=self.run.run_id,
            node_id=node_id,
            state="AWAITING_APPROVAL",
            artifact=artifact
        )
        
        # STOP: Do not proceed downstream
        # Execution will resume when approval event received
        return  # Early return, downstream waits
    
    else:
        fsm.transition("pass")
        await self._proceed_downstream(node_id)

# Event handler (runs when human approves)
async def on_human_approved(self, event: HumanApprovedEvent):
    """EventBus handler for approval events."""
    # Load checkpoint
    checkpoint = await self.store.load_execution_checkpoint(
        run_id=event.run_id,
        node_id=event.node_id
    )
    
    if not checkpoint:
        logger.error(f"No checkpoint found for {event.run_id}/{event.node_id}")
        return
    
    # Resume execution
    fsm = self.fsms[event.node_id]
    fsm.state = NodeState.APPROVAL  # Restore state
    
    if event.decision == "approve":
        fsm.transition("approve")
        await self._log_human_feedback(
            run_id=event.run_id,
            node_id=event.node_id,
            feedback=event.feedback
        )
        await self._proceed_downstream(event.node_id)
    else:
        fsm.transition("reject")
        await self._trigger_retry(event.node_id, feedback=event.feedback)
```

**Pros**: Non-blocking, scalable, fault-tolerant  
**Cons**: More complex, requires checkpointing

---

## 📋 Data Models

```python
# cine_mate/core/models.py

class ApprovalRequiredEvent(CineMateEvent):
    """Emitted when a node requires human approval."""
    event_type: str = "approval_required"
    payload: Dict[str, Any] = {
        "preview_url": str,          # Link to preview asset
        "thumbnail_url": str,        # Thumbnail for quick review
        "node_type": str,            # Type of node (img_gen, video_gen)
        "params": Dict[str, Any],    # Generation parameters
        "estimated_cost": float,     # Cost to proceed
        "timeout_seconds": int       # Approval deadline
    }

class HumanApprovedEvent(CineMateEvent):
    """Emitted when human provides approval decision."""
    event_type: str = "human_approved"
    payload: Dict[str, Any] = {
        "decision": str,             # "approve" | "reject"
        "feedback": str,             # Human comments
        "approved_by": str,          # User ID
        "approved_at": datetime
    }

class ExecutionCheckpoint(BaseModel):
    """Saved state for resuming after human approval."""
    checkpoint_id: str
    run_id: str
    node_id: str
    state: str                   # "AWAITING_APPROVAL"
    artifact: Artifact           # Generated asset
    created_at: datetime
    expires_at: datetime         # Cleanup old checkpoints

class HumanFeedback(BaseModel):
    """Record of human feedback for learning."""
    feedback_id: str
    run_id: str
    node_id: str
    decision: str                # "approve" | "reject"
    feedback_text: str
    user_id: str
    created_at: datetime
```

---

## 🖥️ UI/CLI Interface

### CLI Command

```bash
# List pending approvals
cinemate approvals list --pending

# Review specific node
cinemate approvals review --run-id run_001 --node-id video_gen_01

# Approve with feedback
cinemate approvals approve --run-id run_001 --node-id video_gen_01 \
  --feedback "Perfect lighting, proceed"

# Reject with feedback
cinemate approvals reject --run-id run_001 --node-id video_gen_01 \
  --feedback "Too dark, increase exposure by 20%"
```

### Web UI (Future)

- Approval queue dashboard
- Side-by-side preview (generated vs reference)
- Quick approve/reject buttons
- Feedback text input
- Batch approval for multiple variants

---

## ⚙️ Configuration

```python
# Node-level configuration
dag.add_node(
    node_id="video_gen_01",
    node_type="video_generation",
    config={
        "requires_human_approval": True,
        "approval_timeout": 7200,  # 2 hours
        "notify_on_complete": ["director@studio.com"],
        "minimum_reviewers": 1,
        "auto_escalate": True  # Escalate if timeout
    }
)

# Global configuration
CINEMATE_CONFIG = {
    "hitl": {
        "enabled": True,
        "default_timeout": 3600,
        "max_retries_on_rejection": 3,
        "auto_approve_on_timeout": False,  # Fail on timeout
        "notification_channels": ["email", "slack", "webhook"]
    }
}
```

---

## 🔄 Integration with Existing Systems

### EventBus Integration

```python
# cine_mate/infra/event_bus.py

# Subscribe to approval events
await event_bus.subscribe("approval_required", approval_handler)
await event_bus.subscribe("human_approved", resume_handler)
```

### JobQueue Integration

When human approval is required:
1. Job completes → Generate preview
2. Publish `approval_required` event
3. JobQueue marks job as "AWAITING_APPROVAL"
4. Worker picks up other jobs
5. On `human_approved` event → Resume downstream jobs

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Approval latency | < 5 min median | Time from request to decision |
| Timeout rate | < 10% | Approvals missed due to timeout |
| Rejection rate | TBD | % of nodes rejected (quality indicator) |
| Retry success | > 70% | Rejected nodes that pass on retry |
| User satisfaction | > 4.5/5 | Post-approval survey |

---

## 🗂️ Implementation Tasks

### Phase 1: Core Infrastructure (Sprint 3)
- [ ] Update `NodeExecution` model with approval fields
- [ ] Implement `ExecutionCheckpoint` storage in Store
- [ ] Add approval event handlers to EventBus
- [ ] Update Orchestrator with `on_human_approved` handler

### Phase 2: CLI Interface (Sprint 3)
- [ ] Implement `cinemate approvals list` command
- [ ] Implement `cinemate approvals review` command
- [ ] Implement `cinemate approvals approve/reject` commands
- [ ] Add approval status to `cinemate status` output

### Phase 3: Notifications (Sprint 4)
- [ ] Email notification on approval required
- [ ] Slack integration
- [ ] Webhook support for external systems

### Phase 4: Web UI (Sprint 5+)
- [ ] Approval queue dashboard
- [ ] Preview player integration
- [ ] Batch approval interface
- [ ] Feedback analytics

---

## 🚨 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Long approval delays block pipeline | High | Async design + timeout + escalation |
| Missing checkpoint on crash | Medium | Persistent storage + recovery job |
| Concurrent approvals conflict | Low | Row-level locking in Store |
| Notification fatigue | Medium | Batch notifications, smart filtering |

---

## 🔗 Related Issues

- #X (EventBus implementation) - Dependency
- #Y (Checkpoint/Recovery system) - Dependency
- #Z (Notification system) - Future integration

---

## 📝 Notes

**Current FSM Support**: Already present in `fsm.py`
```python
NodeState.QUALITY_CHECK  # Line 13
NodeState.APPROVAL       # Line 14
transition("review")     # Line 68
transition("approve")    # Line 70
transition("reject")     # Line 71
```

**Decision**: Option B (Async Event-Driven) recommended for production use. Option A can be used for MVP/CLI-only workflows.

---

/cc @hermes @copaw @claude

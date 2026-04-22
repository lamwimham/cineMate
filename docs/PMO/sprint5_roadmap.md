# Sprint 5 Roadmap - MVP Release + HITL Foundation

> **Sprint**: Sprint 5
> **Duration**: 2026-04-27 ~ 2026-05-03 (6 days)
> **Theme**: MVP Release + Human-in-the-Loop (HITL) Foundation
> **Author**: PM (Qwen)
> **Date**: 2026-04-22

---

## 📋 Sprint 5 Overview

### Goals

1. **MVP Release v0.1.0** - 完成发布流程
2. **HITL Foundation** - 实现 Issue #3 核心功能
3. **E2E 测试优化** - 修复 PR #59 遗留问题
4. **Demo 录制** - MVP Demo 视频制作

---

## 🎯 Sprint 5 Objectives

| Objective | Priority | Assignee | Status |
|-----------|----------|----------|--------|
| MVP Release v0.1.0 | P0 | PM | 📋 Pending |
| HITL Core Implementation | P0 | Hermes + Copaw | 📋 Pending |
| E2E Test Optimization | P1 | Copaw | 📋 Pending |
| MVP Demo Recording | P1 | Hermes | 📋 Pending |
| Sprint 4 Final Review | P2 | PM | 📋 Pending |

---

## 📊 Sprint 4 状态回顾

### 完成情况

| Issue | 状态 | PR | Grade |
|-------|------|-----|-------|
| #49 | ✅ Closed | #55 | A+ |
| #50 | ✅ Closed | #56 | A+ |
| #51 | ✅ Closed | #57 | A+ |
| #52 | ✅ Closed | #58 | A+ |
| #53 | ✅ Closed | #59 | A |
| #54 | 📋 Open | - | - |

### MVP 功能状态

| 模块 | 状态 | 测试覆盖率 |
|------|------|------------|
| Engine | ✅ 完成 | 81% |
| Infra | ✅ 完成 | 77% |
| Adapters | ✅ 完成 | 75% |
| Agents | ✅ 完成 | 70% |
| Skills | ✅ 完成 | 85% |
| UI | ✅ 完成 | ⏳ 待测试 |
| API | ✅ 完成 | ✅ 18/18 |

---

## 🚀 Sprint 5 Issue 规划

### Day 1-2: MVP Release Preparation

| Issue | Title | Priority | Assignee | Duration |
|-------|-------|----------|----------|----------|
| #55 | MVP Release v0.1.0 发布 | P0 | PM | 2h |
| #56 | Version Tag + CHANGELOG | P0 | Copaw | 1h |
| #57 | GitHub Release Draft | P0 | PM | 1h |

### Day 3-4: HITL Foundation

| Issue | Title | Priority | Assignee | Duration |
|-------|-------|----------|----------|----------|
| #58 | HITL FSM 状态扩展 | P0 | Hermes | 4h |
| #59 | ApprovalCheckpoint 存储 | P0 | Copaw | 3h |
| #60 | CLI Approvals 命令 | P0 | Hermes | 3h |
| #61 | EventBus Approval 事件 | P0 | Copaw | 2h |

### Day 5: E2E Test Optimization + Demo

| Issue | Title | Priority | Assignee | Duration |
|-------|-------|----------|----------|----------|
| #62 | E2E 异步写入优化 | P1 | Copaw | 3h |
| #63 | MVP Demo 录制 | P1 | Hermes | 4h |

### Day 6: Sprint Review + Documentation

| Issue | Title | Priority | Assignee | Duration |
|-------|-------|----------|----------|----------|
| #64 | Sprint 5 Review Demo | P2 | PM | 2h |
| #65 | Sprint 6 Planning | P2 | PM | 2h |

---

## 🔄 HITL (Issue #3) 规划

### 架构分析

**现有支持**:
- FSM 已有 `QUALITY_CHECK` 和 `APPROVAL` 状态
- EventBus 支持事件订阅
- JobQueue 支持异步任务

**需要新增**:
- Orchestrator pause-and-wait 机制
- ApprovalCheckpoint 数据模型
- CLI approval 命令
- Web UI approval queue (Sprint 6+)

### Phase 1: Core Infrastructure (Sprint 5 Day 3-4)

| Task | Description | File | Assignee |
|------|-------------|------|----------|
| FSM 扩展 | 添加 `AWAITING_APPROVAL` 状态 | `engine/fsm.py` | Hermes |
| Orchestrator Handler | `on_human_approved` 回调 | `engine/orchestrator.py` | Hermes |
| ApprovalCheckpoint Model | 新增数据模型 | `core/store.py` | Copaw |
| EventBus Events | `approval_required`, `human_approved` | `infra/event_bus.py` | Copaw |
| Store Integration | Checkpoint 存储方法 | `core/store.py` | Copaw |

### Phase 2: CLI Interface (Sprint 5 Day 4)

| Task | Description | File | Assignee |
|------|-------------|------|----------|
| Approvals List | `cinemate approvals list --pending` | `cli/approvals.py` | Hermes |
| Approvals Review | `cinemate approvals review --run-id --node-id` | `cli/approvals.py` | Hermes |
| Approvals Approve/Reject | 命令实现 | `cli/approvals.py` | Hermes |

### Phase 3: Notifications (Sprint 6)

- Email notification
- Slack integration
- Webhook support

### Phase 4: Web UI (Sprint 7+)

- Approval queue dashboard
- Preview player integration
- Batch approval interface

---

## 📝 HITL Implementation Details

### FSM State Transition

```
[EXECUTING] → [AWAITING_APPROVAL] → (human decision)
                                      ↓
                   [APPROVED → SUCCEEDED] 或 [REJECTED → RETRY]
```

### ApprovalCheckpoint Model

```python
class ApprovalCheckpoint(BaseModel):
    checkpoint_id: str
    run_id: str
    node_id: str
    state: str  # "AWAITING_APPROVAL"
    artifact: Artifact  # Generated asset
    created_at: datetime
    expires_at: datetime  # Cleanup old checkpoints
```

### EventBus Events

```python
# 新增事件类型
EventTypes.APPROVAL_REQUIRED = "approval_required"
EventTypes.HUMAN_APPROVED = "human_approved"
EventTypes.HUMAN_REJECTED = "human_rejected"
```

### CLI Commands

```bash
# 查看待审批节点
cinemate approvals list --pending

# 审批节点
cinemate approvals review --run-id run_001 --node-id video_gen_01

# 批准
cinemate approvals approve --run-id run_001 --node-id video_gen_01 \
  --feedback "Perfect lighting, proceed"

# 拒绝
cinemate approvals reject --run-id run_001 --node-id video_gen_01 \
  --feedback "Too dark, increase exposure by 20%"
```

---

## 🧪 测试计划

### HITL 测试用例

| Test | Description | Priority |
|------|-------------|----------|
| FSM State Transition | AWAITING_APPROVAL → APPROVED/REJECTED | P0 |
| ApprovalCheckpoint Storage | CRUD 操作 | P0 |
| CLI Commands | List/Review/Approve/Reject | P0 |
| EventBus Events | 事件订阅和发布 | P1 |
| Timeout Handling | 审批超时处理 | P1 |

### 测试覆盖率目标

| 模块 | 当前 | 目标 | Sprint 5 目标 |
|------|------|------|---------------|
| Engine | 81% | 85% | 83% |
| Infra | 77% | 85% | 80% |
| HITL | 0% | 80% | 70% |
| **总体** | **77%** | **85%** | **80%** |

---

## 📊 成功指标

### MVP Release

| Metric | Target |
|--------|--------|
| GitHub Release 创建 | ✅ v0.1.0 |
| 测试覆盖率 | ≥ 80% |
| Demo 视频时长 | ≥ 3 分钟 |
| 用户手册完整性 | 100% |

### HITL Foundation

| Metric | Target |
|--------|--------|
| FSM 状态扩展 | ✅ AWAITING_APPROVAL |
| CLI 命令实现 | ✅ 4 个命令 |
| EventBus 事件 | ✅ 3 个事件类型 |
| 测试通过率 | ≥ 90% |

---

## 🚨 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| HITL 架构复杂度高 | Medium | 分 Phase 实现，Phase 1 专注核心 |
| E2E 测试异步问题 | Low | Sprint 5 Day 5 专项优化 |
| Demo 录制时间不足 | Medium | 提前准备 Demo 脚本和预生成视频 |
| MVP Release 延期 | High | 严格控制 P0 Issue 完成时间 |

---

## 📅 Sprint 5 Calendar

| Day | Date | Focus | Issues |
|-----|------|-------|--------|
| Day 1 | 2026-04-27 | MVP Release Prep | #55, #56, #57 |
| Day 2 | 2026-04-28 | MVP Release + Review | #55, #56, #57 |
| Day 3 | 2026-04-29 | HITL Core | #58, #59, #60, #61 |
| Day 4 | 2026-04-30 | HITL CLI | #60, #61 |
| Day 5 | 2026-05-01 | E2E + Demo | #62, #63 |
| Day 6 | 2026-05-02 | Sprint Review | #64, #65 |

---

## 📞 Team Assignments

| Member | Role | Sprint 5 Focus |
|--------|------|----------------|
| PM (Qwen) | PM | MVP Release + Sprint Planning |
| Hermes | Agent/Gateway/Web | HITL FSM + CLI + Demo |
| Copaw | Infra/Skill | ApprovalCheckpoint + EventBus + E2E |

---

## ✅ Sprint 5 启动条件

| Condition | Status |
|-----------|--------|
| Sprint 4 Issues #49-#53 Closed | ✅ Done |
| MVP 功能验收完成 | ✅ Done |
| 用户手册完成 | ✅ Done |
| Release Checklist 完成 | ✅ Done |

---

## 📝 Sprint 5 交付物

1. **MVP Release v0.1.0**
   - GitHub Release
   - CHANGELOG
   - Git Tag

2. **HITL Foundation**
   - FSM 状态扩展
   - ApprovalCheckpoint 存储
   - CLI Approvals 命令
   - EventBus Approval 事件

3. **E2E Test Optimization**
   - 异步写入修复
   - 13/13 tests PASSED

4. **MVP Demo Video**
   - 3+ 分钟视频
   - GIF for README

---

**Author**: PM (Qwen)
**Date**: 2026-04-22
**Status**: 📋 Draft - Pending Team Approval
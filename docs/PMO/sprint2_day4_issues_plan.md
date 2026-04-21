# Sprint 2 Day 4 Issues 规划

> **PM**: AI Assistant
> **日期**: 2026-04-24 (Day 3 结束后)
> **下一阶段**: Sprint 2 Day 4 (2026-04-25)

---

## 📋 Issue 规划清单

### 🔴 P0 级 Issues (阻塞 Sprint 进度)

| Issue # | 标题 | 助手 | 预估工时 | 交付物 |
|---------|------|------|----------|--------|
| Issue #18 | Python 环境修复 - pytest 无法导入 networkx | Hermes + Copaw | 1h | venv 配置完成 |

### 🟡 P1 级 Issues (重要但非阻塞)

| Issue # | 标题 | 助手 | 预估工时 | 交付物 |
|---------|------|------|----------|--------|
| Issue #19 | Sprint 2 测试覆盖率报告 | Claude | 1.5h | docs/testing/sprint2_coverage_report.md |
| Issue #20 | Sprint 2 整体代码审查报告 | Copaw | 2h | docs/PMO/sprint2_code_review.md |

### 🟢 P2 级 Issues (可选/优化)

| Issue # | 标题 | 助手 | 预估工时 | 交付物 |
|---------|------|------|----------|--------|
| Issue #21 | Sprint 2 Demo 脚本准备 | Hermes | 1h | scripts/demo_sprint2.py |
| Issue #22 | Sprint 2 Demo 流程文档 | Hermes | 0.5h | docs/demo/sprint2_demo_guide.md |

---

## 🔄 工作流程

### 流程图

```
┌──────────────┐
│ PM 定义任务  │
│ 创建 Issue   │
│ 分配人员     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 开发人员     │
│ 领取任务     │
│ 开发实现     │
│ 提交 PR      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PM 审查代码  │
│ Review PR    │
│ 合并 PR      │
│ 关闭 Issue   │
└──────────────┘
```

### Issue → PR → Merge 流程

| 步骤 | 操作 | 负责人 | 时间 |
|------|------|--------|------|
| 1 | 创建 Issue + 分配 | PM | Day 4 开始前 |
| 2 | 开发人员领取任务 | 开发人员 | Day 4 09:00 |
| 3 | 开发实现 | 开发人员 | Day 4 09:00-14:00 |
| 4 | 提交 PR | 开发人员 | Day 4 14:00-15:00 |
| 5 | PM Review | PM | Day 4 15:00-16:00 |
| 6 | 合并 PR + 关闭 Issue | PM | Day 4 16:00-17:00 |

---

## 📋 Issue 详情

### Issue #18: Python 环境修复 (🔴 P0)

**标题**: `P0: Fix Python environment - pytest cannot import networkx`

**助手**: Hermes + Copaw

**问题描述**:
- Python 环境 mismatch 导致 pytest 无法导入 networkx
- pytest 运行在 hermes-agent venv
- networkx 安装在用户级 Python 3.9

**解决方案**:
- 方案 1: 创建项目级 venv (推荐)
- 方案 2: 在现有 venv 安装依赖

**验收标准**:
- `pytest tests/` 可正常运行
- `pytest tests/unit/adapters/` 全通过

---

### Issue #19: 测试覆盖率报告 (🟡 P1)

**标题**: `P1: Generate Sprint 2 test coverage report`

**助手**: Claude

**问题描述**:
- Sprint 2 完成后需要生成测试覆盖率报告
- 验证整体覆盖率是否 >80%
- 验证 Provider 模块覆盖率是否 >90%

**交付物**:
- `docs/testing/sprint2_coverage_report.md`
- 覆盖率 HTML 报告

**验收标准**:
- pytest tests/ 全通过
- 覆盖率报告生成完成

---

### Issue #20: 整体代码审查报告 (🟡 P1)

**标题**: `P1: Sprint 2 comprehensive code review`

**助手**: Copaw

**问题描述**:
- Sprint 2 完成 6 个 PR，需要对整体代码进行审查
- 检查 Provider 适配器架构一致性
- 检查 Worker + Provider 集成正确性

**审查范围**:
- Config System
- EventBus + JobQueue + Worker
- Provider Adapter (base + factory + providers)
- Engine (DAG/FSM)

**交付物**:
- `docs/PMO/sprint2_code_review.md`
- `docs/PMO/sprint2_architecture_health.md`

**验收标准**:
- 审查报告完成
- 健康度评分完成

---

### Issue #21: Demo 脚本准备 (🟢 P2)

**标题**: `P2: Create Sprint 2 demo script`

**助手**: Hermes

**问题描述**:
- Sprint 2 Review Demo 需要演示脚本
- 演示 Provider Factory + Agent + Worker 集成

**Demo 内容**:
1. Provider Factory 创建 Kling + Runway
2. text_to_video 生成流程
3. Worker + Provider 集成

**交付物**:
- `scripts/demo_sprint2.py`

**验收标准**:
- Demo 脚本可运行
- 输出清晰易懂

---

### Issue #22: Demo 流程文档 (🟢 P2)

**标题**: `P2: Create Sprint 2 demo guide document`

**助手**: Hermes

**问题描述**:
- Sprint 2 Review Demo 需要流程文档
- 指导演示流程和时间分配

**文档内容**:
- Demo 流程步骤
- 每个步骤时间分配
- Q&A 预设问题

**交付物**:
- `docs/demo/sprint2_demo_guide.md`

**验收标准**:
- Demo 文档完成
- 流程清晰

---

## 📊 Issue 分配矩阵

| Issue | 标题 | 助手 | 优先级 | 依赖 |
|-------|------|------|--------|------|
| #18 | Python 环境修复 | Hermes + Copaw | 🔴 P0 | 无 |
| #19 | 测试覆盖率报告 | Claude | 🟡 P1 | #18 |
| #20 | 代码审查报告 | Copaw | 🟡 P1 | #18 |
| #21 | Demo 脚本 | Hermes | 🟢 P2 | #18 |
| #22 | Demo 文档 | Hermes | 🟢 P2 | #21 |

**依赖关系**:
- Issue #18 (P0) 必须先完成
- Issue #19, #20, #21 依赖 #18
- Issue #22 依赖 #21

---

## 📅 执行时间表

| 时间 | Issue | 操作 | 助手 |
|------|-------|------|------|
| 09:00 | #18 | 环境修复开发 | Hermes + Copaw |
| 10:00 | #18 | 提交 PR | Hermes + Copaw |
| 10:30 | #18 | PM Review + Merge + Close Issue | PM (Qwen) |
| 11:00 | #19 | 测试覆盖率开发 | Claude |
| 11:00 | #20 | 代码审查开发 | Copaw |
| 14:00 | #19, #20 | 提交 PR | Claude + Copaw |
| 15:00 | #19, #20 | PM Review + Merge + Close Issue | PM (Qwen) |
| 15:00 | #21, #22 | Demo 开发 | Hermes |
| 16:00 | #21, #22 | 提交 PR | Hermes |
| 17:00 | #21, #22 | PM Review + Merge + Close Issue | PM (Qwen) |

---

## 🔄 PR → Issue 关联

每个 PR 需要在描述中关联 Issue：

```markdown
## Related Issue

Fixes #5

## Summary

- 修复 Python 环境 mismatch
- 创建项目级 venv
- 安装 pyproject.toml 依赖
- pytest tests/ 全通过
```

合并 PR 后，Issue 自动关闭。

---

**签名**: PM (AI Assistant)
**日期**: 2026-04-24
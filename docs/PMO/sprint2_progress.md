# Sprint 2 Progress Tracker

> **Sprint**: 2 (2026-04-22 ~ 2026-04-28)
> **目标**: 真实 Agent 调用 + Provider 集成 + CI/CD
> **更新日期**: 2026-04-22

---

## 📊 Sprint 2 目标

| 目标 | 状态 | 备注 |
|------|------|------|
| 真实 Agent 调用 | ⏳ | Day 2-3 |
| Provider 适配器 | ⏳ | Day 3-4 |
| CI/CD GitHub Actions | ⏳ | Day 1 |
| 测试覆盖率 >90% | ⏳ | Day 2 |

---

## 📅 Day 1 进度 (2026-04-22)

| 时间 | 事项 | 状态 | Owner | 备注 |
|------|------|------|-------|------|
| 09:00 | Sprint 2 Kickoff | ✅ | PM | 文档已发布 |
| 09:30 | Day 1 任务下发 | ✅ | PM | hermes/copaw/claude 任务文档 |
| 09:30 | P0 问题修复开始 | ⏳ | hermes | 5 个 P0 问题 |
| 09:30 | CI/CD GitHub Actions | ⏳ | claude | `.github/workflows/test.yml` |
| 11:00 | 接口对齐会议 | ⏳ | hermes + copaw | JobQueue/EventBus 接口 |
| 14:00 | Issue #4 Mock Mode 修复 | ⏳ | hermes | NotImplementedError |
| 17:00 | Daily Standup | ⏳ | 全员 | 进度汇报 |

---

## 📋 遗留问题跟踪

### P0 问题修复 (Day 1)

| # | 问题 | 状态 | Owner | 验收 |
|---|------|------|-------|------|
| 1 | DirectorAgent 硬编码依赖 | ⏳ | hermes | 依赖注入 model 参数 |
| 2 | EngineTools 直接实例化 Store | ⏳ | hermes | 依赖注入 store 参数 |
| 3 | EngineTools 未使用 JobQueue | ⏳ | hermes | 集成 JobQueue.submit_job() |
| 4 | Orchestrator 未发布完成事件 | ⏳ | hermes | 添加 event_bus.publish() |
| 5 | Orchestrator 未订阅事件 | ⏳ | hermes | 添加 event_bus.subscribe() |

### Issue 状态

| Issue | 内容 | 状态 | Owner | Sprint 2 计划 |
|-------|------|------|-------|---------------|
| #4 | Mock Mode 不可测试 | ⏳ | hermes | Day 1 修复 |
| #3 | HITL Feature Request | 🟢 Open | - | Sprint 3+ |

### CI/CD 状态

| 任务 | 状态 | Owner | 备注 |
|------|------|-------|------|
| `.github/workflows/test.yml` | ⏳ | claude | Day 1 |
| Redis service container | ⏳ | claude | Day 1 |
| pytest + coverage | ⏳ | claude | Day 1 |

---

## 📊 成员任务跟踪

### hermes (Agent/Gateway)

| Day | 任务 | 状态 | 验收 |
|-----|------|------|------|
| Day 1 | 修复 5 个 P0 问题 | ⏳ | 依赖注入 + JobQueue 集成 |
| Day 1 | Issue #4 Mock Mode | ⏳ | Mock 模式可测试 |
| Day 2 | 配置系统完整实现 | ⏳ | env 覆盖 + API Key 验证 |
| Day 2-3 | 真实 Agent 调用 | ⏳ | DashScope API |
| Day 3 | Provider 适配器 | ⏳ | 3+ Provider |

---

### copaw (Infra/Skill)

| Day | 任务 | 状态 | 验收 |
|-----|------|------|------|
| Day 1 | 接口对齐会议 | ⏳ | JobQueue/EventBus 接口确认 |
| Day 3 | Provider 适配器设计 | ⏳ | ADR 文档 |
| Day 3-4 | Provider 适配器实现 | ⏳ | 代码实现 |

---

### claude (QA/Testing)

| Day | 任务 | 状态 | 验收 |
|-----|------|------|------|
| Day 1 | CI/CD GitHub Actions | ⏳ | workflow 运行成功 |
| Day 2 | 测试覆盖率提升 (>90%) | ⏳ | coverage report |
| Day 3 | Provider 适配器测试 | ⏳ | 单元测试 |

---

## 📝 PR 跟踪

| PR | 内容 | 状态 | Owner | Sprint 2 |
|----|------|------|-------|----------|
| - | P0 问题修复 | ⏳ | hermes | Day 1 |
| - | CI/CD GitHub Actions | ⏳ | claude | Day 1 |
| - | Issue #4 修复 | ⏳ | hermes | Day 1 |

---

## 🚨 风险跟踪

| Risk ID | 描述 | 状态 | 缓解措施 |
|---------|------|------|----------|
| S2-R1 | DashScope API Key 缺失 | ⏳ | .env 注入 |
| S2-R2 | Provider API 响应慢 | ⏳ | timeout + retry |
| S2-R3 | CI/CD 环境配置失败 | ⏳ | Docker Redis |
| S2-R4 | 测试覆盖率难以提升 | ⏳ | Infra 测试优先 |

---

## 📞 Daily Standup 模板

```markdown
**Name**: hermes / copaw / claude
**Date**: 2026-04-XX (Day X)
**Yesterday**: [昨天完成了什么]
**Today**: [今天计划做什么]
**Blockers**: [有什么阻塞]
```

---

**Prepared by**: PM (AI Assistant)
**Last Updated**: 2026-04-22
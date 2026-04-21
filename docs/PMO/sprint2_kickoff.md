# Sprint 2 Kickoff

> **Sprint**: 2 (2026-04-22 ~ 2026-04-28)
> **目标**: 真实 Agent 调用 + Provider 集成 + CI/CD
> **启动日期**: 2026-04-22
> **团队**: hermes (Agent/Gateway), copaw (Infra/Skill), claude (QA/Testing), PM (AI Assistant)

---

## 📋 Sprint 1 遗留问题 (Day 1 首要任务)

### P0 问题修复 (来自 copaw Code Review)

| # | 问题 | 影响 | Owner | 预估 |
|---|------|------|-------|------|
| 1 | DirectorAgent 硬编码 DashScopeChatModel | 无法 Mock 测试 | hermes | 1h |
| 2 | EngineTools 直接实例化 Store | 无法 Mock Store | hermes | 1h |
| 3 | EngineTools 未使用 JobQueue | 与 Sprint 1 Infra 不兼容 | hermes | 2h |
| 4 | Orchestrator 未发布完成事件 | EventBus 不工作 | hermes | 1h |
| 5 | Orchestrator 未订阅事件 | Event-Driven 不完整 | hermes | 1h |

**来源**: `docs/review/code_review_hermes_agents.md`

### Issue #4 修复

| Issue | 问题 | Owner | 预估 |
|-------|------|-------|------|
| #4 | Mock Mode 不可测试 (NotImplementedError) | hermes | 2h |

### CI/CD 配置

| 任务 | 内容 | Owner | 预估 |
|------|------|-------|------|
| GitHub Actions | pytest + coverage + ruff | claude | 2h |

---

## 🎯 Sprint 2 目标

### 核心目标

1. **真实 Agent 调用**: 取代 Mock Agent，接入 DashScope API
2. **Provider 适配器模式**: 支持 Kling/Runway/Luma 等多厂商
3. **CI/CD 自动化**: GitHub Actions 测试流水线
4. **测试覆盖率提升**: >90%

### 成功标准

| 标准 | 目标 | 验证方式 |
|------|------|----------|
| 真实 Agent 调用成功 | DashScope API 正常响应 | Demo 演示 |
| Provider 适配器 | 支持 3+ Provider | 单元测试 |
| CI/CD 运行 | GitHub Actions 自动测试 | PR 自动触发 |
| 测试覆盖率 | >90% | coverage report |

---

## 📅 Sprint 2 日程规划

### Day 1 (周一) - P0 修复 + CI/CD

| 时间 | 活动 | 参与者 |
|------|------|--------|
| 09:00 | Sprint 2 Kickoff | 全员 |
| 09:30 | P0 问题修复开始 | hermes |
| 09:30 | CI/CD GitHub Actions | claude |
| 11:00 | 接口对齐会议 | hermes + copaw |
| 14:00 | Issue #4 Mock Mode 修复 | hermes |
| 17:00 | Daily Standup | 全员 |

**交付物**:
- hermes: 5 个 P0 问题修复 PR
- claude: CI/CD GitHub Actions PR
- hermes: Issue #4 修复

---

### Day 2 (周二) - 配置系统 + 真实 Agent

| 时间 | 活动 | 参与者 |
|------|------|--------|
| 09:00 | 配置系统完整实现 | hermes |
| 09:00 | 测试覆盖率提升 | claude |
| 14:00 | 真实 Agent 调用开始 | hermes |
| 17:00 | Daily Standup | 全员 |

**交付物**:
- hermes: 配置系统完整 (env 覆盖 + API Key 验证)
- hermes: 真实 Agent 调用 Demo
- claude: 测试覆盖率 >90%

---

### Day 3 (周三) - Provider 适配器

| 时间 | 活动 | 参与者 |
|------|------|--------|
| 09:00 | Provider 适配器设计 | hermes + copaw |
| 14:00 | Provider 适配器实现 | hermes |
| 17:00 | Daily Standup | 全员 |

**交付物**:
- hermes + copaw: Provider 适配器 ADR
- hermes: Provider 适配器实现

---

### Day 4 (周四) - 集成测试 + Review

| 时间 | 活动 | 参与者 |
|------|------|--------|
| 09:00 | 真实 Agent + Provider 集成测试 | hermes + copaw |
| 14:00 | Code Review | 全员 |
| 17:00 | Daily Standup | 全员 |

**交付物**:
- 集成测试报告
- Code Review 反馈

---

### Day 5 (周五) - Sprint Review

| 时间 | 活动 | 参与者 |
|------|------|--------|
| 09:00 | Demo 准备 | hermes |
| 14:00 | 最终验收 | 全员 |
| 16:00 | Go/No-Go | 全员 |
| 17:00 | Sprint Review Demo | 全员 |
| 18:00 | Retrospective | 全员 |

**交付物**:
- Sprint 2 Demo
- Go/No-Go 决策
- Sprint 2 Final Report

---

## 📋 成员任务分配

### hermes (Agent/Gateway)

| Day | 任务 | 预估 | 优先级 |
|-----|------|------|--------|
| Day 1 | 修复 5 个 P0 问题 | 6h | P0 |
| Day 1 | Issue #4 Mock Mode | 2h | P0 |
| Day 2 | 配置系统完整实现 | 4h | P0 |
| Day 2-3 | 真实 Agent 调用 | 6h | P0 |
| Day 3 | Provider 适配器 | 4h | P1 |
| Day 4 | 集成测试 | 2h | P1 |
| Day 5 | Demo 准备 | 4h | P0 |

---

### copaw (Infra/Skill)

| Day | 任务 | 预估 | 优先级 |
|-----|------|------|--------|
| Day 1 | 接口对齐会议 | 1h | P0 |
| Day 3 | Provider 适配器设计 | 4h | P1 |
| Day 3-4 | Provider 适配器实现 | 4h | P1 |
| Day 4 | Code Review | 2h | P1 |
| Day 5 | Sprint Review | 2h | P0 |

---

### claude (QA/Testing)

| Day | 任务 | 预估 | 优先级 |
|-----|------|------|--------|
| Day 1 | CI/CD GitHub Actions | 2h | P0 |
| Day 2 | 测试覆盖率提升 (>90%) | 4h | P1 |
| Day 3 | Provider 适配器测试 | 2h | P1 |
| Day 4 | 集成测试 | 2h | P1 |
| Day 5 | 测试报告 | 2h | P0 |

---

## 📂 文件结构规划

### Sprint 2 新增文件

```
cine_mate/
├── adapters/                   # Provider 适配器 (新增)
│   ├── __init__.py
│   ├── base.py                 # BaseProvider 抽象类
│   ├── kling_adapter.py        # Kling API 适配
│   ├── runway_adapter.py       # Runway API 适配
│   └── luma_adapter.py         # Luma API 适配
├── config/
│   ├── loader.py               # 完整实现 (env 覆盖)
│   └── validator.py            # API Key 验证 (新增)
└── agents/
    ├── director_agent.py       # 修复 P0 问题
    └── tools/
        └── engine_tools.py     # 修复 P0 问题 (JobQueue 集成)

.github/
└── workflows/
    └── test.yml                # CI/CD (新增)

docs/
└── adr/
    └── ADR-003_provider_adapter.md  # Provider 适配器设计 (新增)
```

---

## 🚨 风险与应对

| Risk ID | 描述 | Owner | 缓解措施 |
|---------|------|-------|----------|
| S2-R1 | DashScope API Key 缺失 | hermes | 使用 .env 注入，配置系统支持 |
| S2-R2 | Provider API 响应慢 | hermes | 添加 timeout + retry |
| S2-R3 | CI/CD 环境配置失败 | claude | Docker 容器化 Redis |
| S2-R4 | 测试覆盖率难以提升 | claude | 优先补充 Infra 测试 |

---

## ✅ 验收标准

### hermes 验收

- [ ] 5 个 P0 问题修复完成
- [ ] Issue #4 Mock Mode 可测试
- [ ] 配置系统完整 (env 覆盖 + API Key 验证)
- [ ] 真实 Agent 调用成功
- [ ] Provider 适配器实现 (3+ Provider)
- [ ] Sprint 2 Demo 演示通过

### copaw 验收

- [ ] Provider 适配器 ADR 完成
- [ ] Provider 适配器测试通过
- [ ] Code Review 完成

### claude 验收

- [ ] CI/CD GitHub Actions 运行成功
- [ ] 测试覆盖率 >90%
- [ ] 测试报告生成

---

## 📞 每日 Standup

### 格式

```markdown
**Name**: hermes / copaw / claude
**Date**: 2026-04-XX (Day X)
**Yesterday**: (昨天完成了什么)
**Today**: (今天计划做什么)
**Blockers**: (有什么阻塞)
```

---

## 📚 参考文档

| 文档 | 路径 |
|------|------|
| Sprint 1 Final Report | `docs/PMO/sprint1_final_report.md` |
| Go/No-Go 决策 | `docs/PMO/sprint1_go_no_go.md` |
| Code Review | `docs/review/code_review_hermes_agents.md` |
| 配置系统骨架 | `cine_mate/config/` (PR #11) |
| Async Interface | `docs/architecture/async_interface.md` |

---

**Sprint 2 启动确认**:

- hermes: ⏳ 待确认
- copaw: ⏳ 待确认
- claude: ⏳ 待确认
- PM: ✅

---

**Prepared by**: PM (AI Assistant)
**Date**: 2026-04-22
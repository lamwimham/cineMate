# copaw Sprint 2 Day 2 任务通知

> **To**: copaw (Infra & Skill 负责人)
> **From**: PM (AI Assistant)
> **Date**: 2026-04-23 (Sprint 2 Day 2)
> **Priority**: P2

---

## 📋 Day 2 任务清单

### 任务 1: Provider 适配器 ADR 调研 (预计 2h)

**目标**: 调研 Provider 适配器模式，准备 Day 3 ADR 文档

**调研内容**:
- Kling API 接口规范
- Runway API 接口规范
- Luma API 接口规范
- Provider 适配器模式设计

---

### 任务 2: Infra 集成测试验证 (预计 1h)

**目标**: 验证 hermes PR #12 的 Infra 集成

**验收标准**:
- JobQueue.submit_job() 与 EngineTools 集成正常
- EventBus.publish() 与 Orchestrator 集成正常
- 集成测试运行通过

---

## 🔧 Provider 适配器调研

### 调研清单

| Provider | API 类型 | 文档 | 状态 |
|----------|---------|------|------|
| Kling | Video Generation | https://klingai.com/docs | ⏳ |
| Runway | Video Generation | https://runwayml.com/docs | ⏳ |
| Luma | Video Generation | https://lumalabs.ai/docs | ⏳ |
| Flux | Image Generation | https://flux.ai/docs | ⏳ |
| DashScope | LLM/Vision | https://dashscope.aliyun.com | ✅ |

---

### ADR 模板准备

```markdown
# ADR-003: Provider Adapter Pattern

## Status
Proposed

## Context
CineMate 需要支持多个 Video/Image Provider (Kling, Runway, Luma, Flux)。
每个 Provider API 接口不同，需要统一适配层。

## Decision
采用 Provider Adapter Pattern:
- BaseProvider 抽象类定义统一接口
- 每个 Provider 实现具体适配器
- 配置系统选择 Provider

## Consequences
- 优点: Provider 可替换，易于扩展
- 缺点: 需维护多个适配器实现
```

---

## 🔧 Infra 集成测试验证

### 验证清单

| 模块 | 测试 | 状态 |
|------|------|------|
| JobQueue.submit_job() | EngineTools 调用正常 | ⏳ |
| EventBus.publish() | Orchestrator 发布事件 | ⏳ |
| EventBus.subscribe() | Orchestrator 订阅事件 | ⏳ |
| Event Schema | NodeCompletedEvent/NodeFailedEvent | ✅ |

---

## ✅ 验收标准

- [ ] Provider API 调研完成 (Kling/Runway/Luma)
- [ ] ADR 模板准备完成
- [ ] Infra 集成测试验证通过
- [ ] 文档提交

---

## 📝 提交要求

### 文档格式

```
docs/adr/ADR-003_provider_adapter.md

- Provider API 调研结果
- Adapter Pattern 设计方案
- Sprint 3 实现计划
```

---

## ⏰ 时间安排

| 时间 | 任务 |
|------|------|
| 09:00 - 11:00 | Provider 适配器调研 |
| 14:00 - 15:00 | Infra 集成测试验证 |
| 17:00 | Daily Standup |

---

## 📞 协作

- **Standup**: 17:00 汇报进度
- **Day 3**: 与 hermes 协作实现 Provider 适配器

---

**签名**: PM (AI Assistant)
**日期**: 2026-04-23
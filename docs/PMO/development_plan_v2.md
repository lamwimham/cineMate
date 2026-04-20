# CineMate 开发计划 v2.0 (PMO 修订版)

> **Version**: 2.0.0 | **PM Approval**: ✅ Active
> **Date**: 2026-04-20 | **Est. Duration**: 10-12 Weeks
> **Status**: Ready for Sprint 1

---

## 执行摘要

本计划基于 v1.0 的反馈进行了以下关键调整：

| 调整项 | v1.0 | v2.0 (修订) | 理由 |
|--------|------|-------------|------|
| **总工期** | 13 工作日 | **50-60 工作日** | 原估算过于乐观，含缓冲 |
| **里程碑数** | 5 个 | **7 个** | 新增 M3.5 (Async Infra) + M6 (Prod Ready) |
| **M2 工期** | 3 天 | **7 天** | Agent 意图解析是核心难点 |
| **M3 工期** | 4 天 | **10 天** | 需包含异步工作流 + 安全加固 |
| **测试策略** | 仅在 M1 | **每个里程碑内嵌** | 质量门禁 |
| **风险管理** | 无 | **Top 5 实时跟踪** | 早期识别 |

---

## 修订后的里程碑总览

```
Week:  1    2    3    4    5    6    7    8    9   10   11   12
       │    │    │    │    │    │    │    │    │    │    │
M1:    └────┤    │    │    │    │    │    │    │    │    │  ✅ 已完成
            │    │    │    │    │    │    │    │    │    │
M2:         └────┴────┤    │    │    │    │    │    │    │  AgentScope
                      │    │    │    │    │    │    │    │
M3.5:                 └────┴────┤    │    │    │    │    │  Async Infra
                                │    │    │    │    │    │
M3:                             └────┴────┴────┴────┤    │  Cloud Gateway
                                                    │    │
M4:                                                 └────┤  Skill System
                                                         │
M5:                                                      ├────  CLI/UI
                                                         │
M6:                                                      └────  Prod Ready

Key Dates:
• v0.1 Alpha:   Week 3 (2026-05-11)
• v0.5 Beta:    Week 8 (2026-06-15)
• v1.0 GA:      Week 12 (2026-07-13)
```

---

## Milestone 1: Core Engine & Video Git ✅ COMPLETED

> **Duration**: 2 Weeks | **Status**: ✅ Done | **Actual**: 2026-04-06 ~ 2026-04-20

### 交付物清单
- [x] `cine_mate/core/models.py` - Pydantic V2 数据模型
- [x] `cine_mate/core/store.py` - Async SQLite + CAS
- [x] `cine_mate/engine/dag.py` - 拓扑排序 + 脏检测
- [x] `cine_mate/engine/fsm.py` - 节点状态机
- [x] `cine_mate/engine/orchestrator.py` - 执行编排
- [x] `tests/test_dirty_propagation.py` - 脏传播测试 (通过)

### 质量验证
| 检查项 | 结果 | 备注 |
|--------|------|------|
| 单元测试 | ✅ 12 个测试通过 | 覆盖率 85% |
| 脏传播逻辑 | ✅ 验证通过 | 增量更新正确识别 |
| 性能测试 | ✅ 100 节点 DAG <50ms | 拓扑排序 |

---

## Milestone 2: AgentScope Integration 🚀 CURRENT

> **Duration**: 7 Days | **Sprint**: Week 1-2 | **Status**: 🟡 Planning
> **Goal**: 验证 "User NL → Agent → Engine" 核心循环可行性

### Phase 2.1: Technical Spike (Days 1-2)
**Goal**: 验证 NL→DAG 意图解析是否可行

| 任务 | 负责人 | 工时 | 产出 |
|------|--------|------|------|
| 安装 AgentScope，跑通 EchoAgent | hermes | 4h | 基础环境 OK |
| 设计 3 种场景的 Prompt 模板 | PM | 4h | `prompts/intent_v1.md` |
| 手动测试 20 个 case，记录准确率 | Dev+PM | 8h | 准确率评估报告 |
| **Go/No-Go 决策会议** | PM | 1h | 决策记录 |

**Go Criteria**:
- NL→DAG 结构准确率 >= 70%
- 或通过 "Agent 建议 + 用户确认" 可达 >= 90%

**No-Go Fallback**:
- 降级为半自动模式：Agent 提供表单建议，用户手动确认/调整

### Phase 2.2: DirectorAgent Core (Days 3-5)
**Goal**: 实现基础 Agent + Engine Toolkit

```python
# 交付物: cine_mate/agents/director_agent.py
class DirectorAgent(ReActAgent):
    """
    系统 Prompt 核心指令:
    1. 你是 CineMate 的 Director Agent，帮助用户创建和修改视频
    2. 你可以使用以下工具：
       - create_pipeline(prompt: str) -> run_id
       - get_run_status(run_id: str) -> status
       - modify_node(run_id: str, node_id: str, params: dict)
       - list_available_skills() -> list
       - apply_skill(run_id: str, skill_name: str)
    3. 用户用自然语言描述需求，你解析为 Engine 可执行的操作
    4. 复杂需求分步骤执行，每步向用户确认
    """
```

| 任务 | 负责人 | 工时 | 验收标准 |
|------|--------|------|----------|
| 实现 `DirectorAgent` 骨架 | hermes | 6h | 可实例化，响应基本指令 |
| 实现 Engine Toolkit (4 个 tools) | hermes | 8h | 每个 tool 有单元测试 |
| 编写 System Prompt v1 | PM | 4h | 覆盖主要场景 |
| 集成测试：Agent + Engine | hermes | 6h | 端到端流程通过 |

### Phase 2.3: Intent Parser v1 (Days 6-7)
**Goal**: 基础意图解析 + 错误处理

| 任务 | 负责人 | 工时 | 验收标准 |
|------|--------|------|----------|
| 实现 `IntentParser` 类 | hermes | 8h | 能提取关键参数 |
| 实现 DAG Builder | hermes | 6h | JSON → DAG 对象 |
| 添加用户确认机制 | hermes | 4h | 模糊意图时主动询问 |
| 编写 20 个测试 case | PM | 4h | 准确率 >70% |
| **里程碑验收** | PM | 2h | 检查清单 |

### M2 质量门禁
- [ ] 单元测试 >80%
- [ ] 20 个真实用户意图 case 测试
- [ ] 错误处理覆盖 (网络/解析/Engine 错误)
- [ ] 文档：`docs/agents/director_agent.md`

---

## Milestone 3.5: Async Infrastructure (NEW) 🆕

> **Duration**: 5 Days | **Sprint**: Week 3-4 | **Status**: ⚪ Not Started
> **Why**: 上游 API 是异步的 (1-5min 生成)，必须先做异步基础设施

### Phase 3.5.1: Job Queue Design (Day 1)

**决策记录** (ADR-001):
```yaml
decision: 使用 Redis + RQ 作为 Job Queue
alternatives:
  - Celery: 功能多但复杂
  - Bull (Node.js): 技术栈不匹配
  -自建: 维护成本高
rationale: RQ 简单，Python 原生，足够满足需求
```

| 任务 | 负责人 | 工时 |
|------|--------|------|
| 设计 Job Queue 架构 | hermes | 4h |
| 定义 Job Schema | PM+Dev | 4h |
| Redis 环境搭建 | hermes | 2h |

### Phase 3.5.2: Webhook System (Days 2-3)

**交付物**: `server/services/webhook.py`

```python
# Webhook 安全设计
class WebhookHandler:
    """
    接收上游 (Kling/Runway) 回调
    安全验证: HMAC-SHA256 + Timestamp
    """
    async def handle_kling_callback(payload: dict, signature: str):
        # 1. 验证签名
        # 2. 验证 timestamp (防重放，5min 窗口)
        # 3. 更新 Job 状态
        # 4. 触发 SSE 推送给客户端
```

| 任务 | 负责人 | 工时 |
|------|--------|------|
| 实现 Webhook Handler (Kling/Runway) | hermes | 8h |
| 实现 HMAC 签名验证 | hermes | 4h |
| 实现重试 + 死信队列 | hermes | 6h |
| Webhook 测试 (Mock 上游) | hermes | 4h |

### Phase 3.5.3: Real-time Push (Day 4)

**交付物**: SSE (Server-Sent Events) 实现

| 任务 | 负责人 | 工时 |
|------|--------|------|
| 实现 SSE Endpoint | hermes | 4h |
| 客户端连接管理 | hermes | 4h |
| 进度推送机制 | hermes | 4h |
| 断线重连处理 | hermes | 4h |

### Phase 3.5.4: Integration & Tests (Day 5)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| 集成 Queue + Webhook + SSE | hermes | 6h |
| 端到端测试 | hermes | 4h |
| 性能测试 (100 并发 jobs) | hermes | 4h |
| **里程碑验收** | PM | 2h |

### M3.5 质量门禁
- [ ] Job Queue 100 并发稳定
- [ ] Webhook 接收成功率 >99.9%
- [ ] SSE 延迟 <500ms
- [ ] 故障恢复测试 (Redis 重启)

---

## Milestone 3: Cloud Gateway MVP

> **Duration**: 10 Days | **Sprint**: Week 4-7 | **Status**: ⚪ Not Started
> **依赖**: M3.5 (Async Infra)
> **Goal**: 生产级网关：Auth + Billing + Routing + Audit

### Phase 3.1: Server Skeleton (Days 1-2)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| FastAPI 项目结构 | hermes | 4h |
| 基础路由: `POST /api/v1/jobs` | hermes | 4h |
| 健康检查 + 指标 | hermes | 4h |
| 结构化日志 (structlog) | hermes | 4h |

### Phase 3.2: Auth System (Days 3-4)

**交付物**: `server/middleware/auth.py`

| 任务 | 负责人 | 工时 |
|------|--------|------|
| API Key 认证 | hermes | 6h |
| JWT Token (User Session) | hermes | 4h |
| Rate Limiting (Redis) | hermes | 6h |
| 权限中间件 | hermes | 4h |

### Phase 3.3: Billing System (Days 5-7)

**关键设计决策**:
```yaml
billing_modes:
  managed:
    - 预付费 Credits 模式
    - 调用前检查余额
    - 调用后扣除 (实际消耗)
    - 支持退款 (失败任务)
  
  byok:
    - 用户自带 API Key
    - 本地 Keychain 存储
    - 发送 Hash 验证权限 (Key 不触网)
    - CineMate 收订阅费，不收流量费
```

| 任务 | 负责人 | 工时 |
|------|--------|------|
| Credits 系统设计 | PM+Dev | 6h |
| Managed 计费实现 | hermes | 8h |
| BYOK 验证实现 | hermes | 8h |
| 审计日志 (PostgreSQL) | hermes | 6h |
| 计费测试 (Mock) | hermes | 4h |

### Phase 3.4: Proxy & Routing (Days 8-9)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| 上游 Provider 抽象 | hermes | 6h |
| Kling 代理实现 | hermes | 6h |
| Runway 代理实现 | hermes | 6h |
| 智能路由 (成本/质量/速度) | hermes | 6h |
| 错误处理 + 熔断 | hermes | 4h |

### Phase 3.5: Security Hardening (Day 10)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| 内容安全审查 (NSFW) | hermes | 4h |
| 输入验证加固 | hermes | 4h |
| 安全扫描 (bandit) | hermes | 2h |
| 渗透测试清单 | PM | 4h |
| **里程碑验收** | PM | 2h |

### M3 质量门禁
- [ ] 安全扫描 0 High/Medium
- [ ] 压力测试: 1000 RPS, P99 <200ms
- [ ] 计费准确性: 100% (财务级)
- [ ] 文档: API 参考 (OpenAPI)

---

## Milestone 4: Style as Skill System

> **Duration**: 5 Days | **Sprint**: Week 8 | **Status**: ⚪ Not Started

### Phase 4.1: Skill Loader (Day 1-2)

**Skill 文件格式** (参考 Anthropic):
```yaml
# skills/wong_kar_wai/SKILL.md
---
name: "Wong Kar-wai Style"
version: "1.0.0"
author: "CineMate Team"
tags: ["cinematic", "neon", "nostalgia"]
default_params:
  color_grading: "teal_orange"
  frame_rate: 24
  motion_blur: 0.3
---

# 系统 Prompt 片段
When applying Wong Kar-wai style:
- Use step-printing for slow-motion scenes
- High contrast neon lighting
- Frame-within-frame compositions
...
```

| 任务 | 负责人 | 工时 |
|------|--------|------|
| Skill Schema 设计 | PM+Dev | 4h |
| YAML Frontmatter 解析 | hermes | 4h |
| Markdown Body 提取 | hermes | 4h |
| 参数合并逻辑 | hermes | 6h |

### Phase 4.2: Dynamic Loading (Day 3)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| 运行时 Skill 加载 | hermes | 6h |
| Skill 缓存机制 | hermes | 4h |
| Skill 版本管理 | hermes | 4h |

### Phase 4.3: Integration (Day 4)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| Agent Skill 命令 | hermes | 6h |
| Engine 参数注入 | hermes | 6h |
| 3 个官方 Skill | PM | 4h |

### Phase 4.4: Tests (Day 5)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| Skill 加载测试 | hermes | 4h |
| 参数合并测试 | hermes | 4h |
| **里程碑验收** | PM | 2h |

---

## Milestone 5: CLI & UI

> **Duration**: 4 Days | **Sprint**: Week 9 | **Status**: ⚪ Not Started

### Phase 5.1: CLI Framework (Day 1)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| Typer CLI 骨架 | hermes | 4h |
| `cinemate --version` | hermes | 2h |
| 配置管理 | hermes | 4h |

### Phase 5.2: Chat Interface (Day 2)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| `cinemate chat` REPL | hermes | 8h |
| Rich 格式化输出 | hermes | 6h |
| 历史记录 | hermes | 4h |

### Phase 5.3: Video Git Visualization (Day 3-4)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| `cinemate log` (git log --graph 风格) | hermes | 8h |
| `cinemate status` | hermes | 4h |
| `cinemate checkout` | hermes | 4h |
| `cinemate diff` | hermes | 4h |

---

## Milestone 6: Production Readiness

> **Duration**: 5 Days | **Sprint**: Week 10-11 | **Status**: ⚪ Not Started

### Phase 6.1: Testing (Day 1-2)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| 单元测试补充 | hermes | 8h |
| 集成测试套件 | hermes | 8h |
| E2E 测试 (Playwright) | hermes | 8h |
| 性能基准 | hermes | 4h |

### Phase 6.2: Observability (Day 3)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| Prometheus Metrics | hermes | 6h |
| Grafana Dashboards | hermes | 6h |
| Sentry Error Tracking | hermes | 4h |
| Alerting Rules | hermes | 4h |

### Phase 6.3: Documentation (Day 4)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| API 文档 (OpenAPI) | hermes | 6h |
| 用户指南 | PM | 8h |
| 部署指南 | hermes | 4h |
| Skill 开发指南 | PM | 4h |

### Phase 6.4: Launch Prep (Day 5)

| 任务 | 负责人 | 工时 |
|------|--------|------|
| CHANGELOG | PM | 2h |
| Release Notes | PM | 4h |
| 部署检查清单 | PM | 4h |
| **v1.0 GA 发布** | Team | 🎉 |

---

## 资源需求

### 人力 (已落实)

| 姓名 | 角色 | 投入时间 | 职责 | 状态 |
|------|------|----------|------|------|
| **hermes** | 全栈开发工程师 | 全职 | 架构、Engine、Agent、Gateway、Skill、CLI | ✅ 已加入 |
| **PM (AI Assistant)** | 项目管理/产品 | 持续 | 规划、跟踪、协调、文档 | ✅ 活跃 |

**团队特点**:
- 小而精: 1 名全栈工程师 + PM
- 全栈覆盖: hermes 负责所有技术实现
- 快速决策: 无跨团队协调成本

#### hermes 技能矩阵

| 领域 | 熟练度 | 备注 |
|------|--------|------|
| Python / FastAPI | ⭐⭐⭐⭐⭐ | 主力语言 |
| AI/ML (Agent/LLM) | ⭐⭐⭐⭐ | AgentScope、Prompt Engineering |
| 数据库 (SQLite/PostgreSQL) | ⭐⭐⭐⭐ | 熟悉 ORM 和优化 |
| DevOps (Docker/CI/CD) | ⭐⭐⭐ | 基础部署能力 |
| Frontend (React/Vue) | ⭐⭐ | 基础前端能力 |

#### hermes 开发路线

| 里程碑 | 周期 | hermes 核心交付物 |
|--------|------|-------------------|
| M2 | Week 1-2 | AgentScope 集成、DirectorAgent、意图解析 |
| M3.5 | Week 3-4 | Redis Job Queue、Webhook、SSE |
| M3 | Week 4-7 | FastAPI Gateway、Auth、Billing、Proxy |
| M4 | Week 8 | Skill System 设计与实现 |
| M5 | Week 9 | CLI Chat、Video Git 可视化 |
| M6 | Week 10-11 | 测试、监控、文档、发布 |

#### 协作原则

1. **Daily Standup**: hermes 每日更新 3 句话（昨晚做了什么 / 今天计划 / 阻塞）
2. **Code Review**: 所有代码需 PM 审查后才能合并
3. **文档同步**: 功能实现同时更新文档
4. **决策升级**: 技术选型 >30min 无法决定时，升级到 PM

### 基础设施

| 资源 | 用途 | 估算成本 |
|------|------|----------|
| Redis (云服务) | Job Queue | $50/月 |
| PostgreSQL | 审计日志 | $30/月 |
| 应用服务器 | Gateway | $100/月 |
| 对象存储 | Blob Store | 按量 |
| 监控 (Grafana Cloud) | 可观测性 | 免费层 |
| Sentry | 错误跟踪 | 免费层 |

---

## 风险与应对 (Top 5)

| ID | 风险 | P | I | Score | Owner | 缓解措施 | 应急方案 |
|----|------|---|---|-------|-------|---------|---------|
| R-001 | NL→DAG 准确率不足 | H | H | 9 | PM | M2 Spike 验证 | 降级半自动模式 |
| R-002 | 上游 API 不稳定 | M | H | 6 | PM | 多供应商策略 | 熔断 + 降级提示 |
| R-003 | 开发进度延迟 | M | M | 4 | PM | 每周 buffer，功能裁剪 | 延期发布，砍低优先级功能 |
| R-004 | 竞品大厂入场 | H | M | 6 | PM | 专注细分 (Video Git) | 加速社区/生态建设 |
| R-005 | 安全漏洞 | M | H | 6 | Tech Lead | 安全扫描，代码审查 | 快速补丁 + 事件响应 |

---

## 附录

### A. 决策记录 (ADRs)

| ID | 决策 | 日期 | 状态 |
|----|------|------|------|
| ADR-001 | 使用 Redis + RQ 作为 Job Queue | 2026-04-20 | Proposed |
| ADR-002 | BYOK 使用 HMAC-SHA256 签名 | 2026-04-20 | Proposed |
| ADR-003 | SSE 替代 WebSocket 用于进度推送 | 2026-04-20 | Proposed |

### B. 术语表

| 术语 | 定义 |
|------|------|
| **Video Git** | 像 Git 一样管理视频创作的版本控制系统 |
| **Dirty Propagation** | 仅重算 DAG 中变更节点及其下游的算法 |
| **CAS** | Content-Addressable Store，内容寻址存储 |
| **BYOK** | Bring Your Own Key，用户自带 API Key |
| **Skill** | 可插拔的风格/能力模块 |

### C. 参考文档

- 架构设计: `docs/architecture.md`
- 商业计划: `docs/CineMate_Business_Plan_v1.0.md`
- 项目章程: `docs/PMO/project_charter.md`

---

**审批状态**: ✅ PM Approved
**下次评审**: 2026-04-27 (每周一 Sprint Planning)

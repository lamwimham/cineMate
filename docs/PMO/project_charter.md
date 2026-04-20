# CineMate 项目管理章程 (Project Charter)

> **Role**: PMO (Project Management Office)
> **PM Lead**: AI Assistant
> **Status**: Active
> **Last Updated**: 2026-04-20

---

## 1. 项目概况

| 项目属性 | 详情 |
|---------|------|
| **项目名称** | CineMate - AI Video Production OS |
| **项目愿景** | 成为 AI 视频制作领域的 "GitHub" —— 版本控制 + 协作 + 生态 |
| **目标市场** | AI 创作者、营销团队、独立制作人 |
| **目标用户** | 1,000 (Year 1) → 10,000 (Year 2) → 50,000+ (Year 3) |
| **关键里程碑** | v0.1 Alpha (Q2) → v0.5 Beta (Q3) → v1.0 GA (Q4) |

---

## 2. 项目管理方法论

### 2.1 采用框架：**敏捷 Scrum + 精益创业**

```
 Sprint Cycle: 1 Week
 ├── Monday: Sprint Planning (1h)
 ├── Daily: Async Standup (Slack/Discord)
 ├── Thursday: Mid-sprint check
 └── Friday: Sprint Review + Retrospective (1h)
```

### 2.2 优先级框架：**MoSCoW + ICE 评分**

| 优先级 | 定义 | 处理策略 |
|--------|------|----------|
| **Must** | 没有就不能发布 | 必须完成，资源优先 |
| **Should** | 重要但可妥协 | 力争完成，可延期 |
| **Could** | 有更好，没有也行 | 有余力再做 |
| **Won't** | 明确不做 | 记录但搁置 |

### 2.3 决策机制：**RACI 矩阵**

| 角色 | 职责 | 人员 |
|------|------|------|
| **R - Responsible** | 执行任务 | hermes, copaw (开发工程师) |
| **A - Accountable** | 最终负责 | PM (AI Assistant) |
| **C - Consulted** | 提供意见 | 架构顾问、用户代表 |
| **I - Informed** | 知情 | 投资人、社区 |

### 2.4 团队成员

| 姓名 | 角色 | 主要职责 | 投入 | 状态 |
|------|------|----------|------|------|
| **hermes** | 全栈开发工程师 | Agent、Cloud Gateway、CLI | 全职 | ✅ 活跃 |
| **copaw** | 全栈开发工程师 | Async Infra、Skill System、DevOps | 全职 | ✅ 新加入 |
| **PM** | 项目管理/产品 | 规划、跟踪、协调、文档 | 持续 | ✅ 活跃 |

#### 团队分工策略

```
CineMate 开发团队 (2人)
═══════════════════════════════════════════════════════════════

hermes (Agent & Gateway 负责人)
├── Milestone 2: AgentScope Integration
│   ├── DirectorAgent 实现
│   ├── Engine Toolkit
│   └── NL→DAG 意图解析
├── Milestone 3: Cloud Gateway
│   ├── FastAPI Server
│   ├── Auth & Billing
│   └── Proxy & Routing
└── Milestone 5: CLI & UI
    └── cinemate chat / log / status

copaw (Infra & Skill 负责人)
├── Milestone 3.5: Async Infrastructure (NEW)
│   ├── Redis Job Queue
│   ├── Webhook System
│   └── SSE Real-time Push
├── Milestone 4: Skill System
│   ├── Skill Loader
│   ├── Dynamic Injection
│   └── Engine Overrides
└── Milestone 6: Production Readiness
    ├── Testing Suite
    ├── Observability (Prometheus/Grafana)
    └── CI/CD Pipeline

协作接口
├── Code Review: 互相 Review + PM 最终审批
├── Async: 通过 Job Queue 解耦 (copaw 提供接口, hermes 调用)
└── Sync: 每周三 Technical Review 对齐架构
```

#### hermes 技能矩阵

| 领域 | 熟练度 | 备注 |
|------|--------|------|
| Python / FastAPI | ⭐⭐⭐⭐⭐ | 主力语言 |
| AI/ML (Agent/LLM) | ⭐⭐⭐⭐ | AgentScope、Prompt Engineering |
| 数据库 (SQLite/PostgreSQL) | ⭐⭐⭐⭐ | 熟悉 ORM 和优化 |
| DevOps (Docker/CI/CD) | ⭐⭐⭐ | 基础部署能力 |
| Frontend (React/Vue) | ⭐⭐ | 基础前端能力 |

#### copaw 技能矩阵

| 领域 | 熟练度 | 备注 |
|------|--------|------|
| Python / FastAPI | ⭐⭐⭐⭐⭐ | 主力语言 |
| 消息队列 (Redis/RabbitMQ) | ⭐⭐⭐⭐⭐ | 高并发、分布式系统 |
| DevOps (K8s/Docker/CI/CD) | ⭐⭐⭐⭐ | 基础设施专家 |
| 监控/可观测性 | ⭐⭐⭐⭐ | Prometheus/Grafana/ELK |
| 数据库 (PostgreSQL/Redis) | ⭐⭐⭐⭐ | 性能优化 |
| AI/ML (Agent/LLM) | ⭐⭐⭐ | 快速学习中 |

#### 协作原则

1. **Daily Standup**: hermes & copaw 各自更新 3 句话（昨晚/今天/阻塞）
2. **Code Review**: 
   - 互相 Review (hermes ↔ copaw)
   - PM 最终审批
   - 关键模块需两人共同 Review
3. **文档同步**: 功能实现同时更新文档
4. **决策升级**: 技术选型 >30min 无法决定时，升级到 PM
5. **接口契约**: 模块间接口需文档化，变更需通知对方

---

## 3. 沟通机制

### 3.1 同步沟通

| 会议 | 频率 | 时长 | 参与人 | 目的 |
|------|------|------|--------|------|
| Sprint Planning | 每周一 | 1h | 全团队 | 计划本周任务 |
| Daily Standup | 每日 | 15min | 开发团队 | 同步进展/阻塞 |
| Technical Review | 每周三 | 1h | 技术负责人 | 代码/架构评审 |
| Sprint Review | 每周五 | 1h | 全团队+Stakeholder | 演示成果 |
| Retrospective | 每周五 | 30min | 全团队 | 持续改进 |

### 3.2 异步沟通

- **GitHub Issues**: 任务跟踪、Bug 报告
- **GitHub Discussions**: 技术决策、RFC
- **Discord/Slack**: 日常沟通、紧急问题
- **Notion/Confluence**: 文档中心
- **Loom**: 异步视频更新 (用于复杂演示)

### 3.3 汇报机制

| 层级 | 频率 | 内容 | 接收人 |
|------|------|------|--------|
| **Daily Update** | 每日 | 3 句话总结 | 团队群 |
| **Weekly Report** | 每周 | 进度、风险、下周计划 | 全团队 |
| **Milestone Report** | 每阶段 | 完整里程碑回顾 | Stakeholder |
| **Monthly Review** | 每月 | 商业指标、用户反馈 | 投资人 |

---

## 4. 风险管理

### 4.1 风险登记册模板

```yaml
risk_id: R-001
name: "Agent 意图解析准确率不足"
probability: High    # Low/Medium/High
impact: High         # Low/Medium/High
score: 9             # 1-9 (P*I)
owner: "PM"
mitigation: "M2 先进行 Spike 验证，不达标则降级为手动辅助"
contingency: "引入 Few-shot Prompting + 用户确认机制"
status: "Active"     # Active/Monitored/Closed
```

### 4.2 Top 5 风险 (实时更新)

| ID | 风险 | P | I | Score | 状态 | 最后更新 |
|----|------|---|---|-------|------|---------|
| R-001 | NL→DAG 准确率不足 | H | H | 9 | 🟡 | 2026-04-20 |
| R-002 | 上游 API 不稳定/涨价 | M | H | 6 | 🟢 | 2026-04-20 |
| R-003 | 开发进度延迟 | M | M | 4 | 🟢 | 2026-04-20 |
| R-004 | 竞品大厂入场 | H | M | 6 | 🟢 | 2026-04-20 |
| R-005 | 资金短缺 | L | H | 3 | 🟢 | 2026-04-20 |

---

## 5. 质量门禁 (Quality Gates)

### 5.1 代码质量

| 检查项 | 工具 | 阈值 | 门禁 |
|--------|------|------|------|
| 单元测试覆盖率 | pytest + coverage | >80% | 🔴 Must Pass |
| 代码风格 | ruff + black | 0 errors | 🔴 Must Pass |
| 类型检查 | mypy | 0 errors | 🟡 Should Pass |
| 安全扫描 | bandit | 0 High/Medium | 🔴 Must Pass |
| 性能回归 | pytest-benchmark | <110% baseline | 🟡 Should Pass |

### 5.2 发布标准 (Definition of Done)

- [ ] 功能完整实现
- [ ] 单元测试覆盖率 >80%
- [ ] 集成测试通过
- [ ] 代码审查通过 (至少 1 人)
- [ ] 文档已更新
- [ ] CHANGELOG 已更新
- [ ] 无 P0/P1 Bug

---

## 6. 度量指标 (Metrics)

### 6.1 工程指标

| 指标 | 目标 | 监控频率 |
|------|------|----------|
| **Velocity** | 每周完成 Story Points | 每周 |
| **Cycle Time** | 任务从开始到完成 <3 天 | 每周 |
| **Bug Escape Rate** | 生产 Bug <5% | 每月 |
| **MTTR** | 平均恢复时间 <2h | 实时 |
| **Uptime** | 服务可用性 >99.9% | 实时 |

### 6.2 产品指标

| 指标 | 目标 | 监控频率 |
|------|------|----------|
| **MAU** | 月活用户增长 | 每周 |
| **Retention** | 7 日留存 >30% | 每月 |
| **NPS** | 净推荐值 >40 | 每季度 |
| **Cost per Video** | 单视频成本趋势 | 每周 |

---

## 7. 项目时间表总览

```
2026 Q2                            2026 Q3                            2026 Q4
Apr        May        Jun          Jul        Aug        Sep          Oct        Nov        Dec
│          │          │            │          │          │            │          │          │
├─ M2 ─────┤          │            ├─ M3 ─────┤          │            │          │          │
│ Agent    │          │            │ Cloud    │          │            │          │          │
│ Scope    │          │            │ Gateway  │          │            │          │          │
│ Spike    │          │            │          │          │            │          │          │
           ├─ M3.5 ───┤            │          ├─ M4 ─────┤            ├─ M5 ─────┤          │
           │ Async    │            │          │ Skill    │            │ CLI/UI   │          │
           │ Infra    │            │          │ System   │            │          │          │
                      ├─ Buffer ───┤          │          ├─ Buffer ───┤          ├─ M6 ─────┤
                      │ (2w)       │          │          │ (2w)       │          │ Prod     │
                                 v0.1 Alpha               v0.5 Beta               v1.0 GA
```

---

## 8. 本周行动项 (Week of 2026-04-20) - Sprint 1

### Sprint 1 Goal: **Validate Agent Intent Parsing Viability**
> **Developer**: hermes | **PM**: AI Assistant | **Duration**: 5 Days

| 任务 ID | 任务 | Owner | 工时 | 截止时间 | 状态 |
|---------|------|-------|------|---------|------|
| S1-001 | 阅读 AgentScope 文档，安装环境 | hermes | 3h | 周一 | 🟡 |
| S1-002 | 跑通 EchoAgent Demo | hermes | 2h | 周一 | ⚪ |
| S1-003 | 设计 NL→DAG Prompt 模板 (3 场景) | PM | 4h | 周二 | 🟡 |
| S1-004 | 准备 20 个测试 case | PM | 2h | 周二 | ⚪ |
| S1-005 | 手动测试 Prompt 准确率 | PM | 2h | 周二 | ⚪ |
| S1-006 | 实现 DirectorAgent 基础类 | hermes | 6h | 周三 | ⚪ |
| S1-007 | 编写 System Prompt | PM | 2h | 周三 | ⚪ |
| S1-008 | 实现 Engine Toolkit (4 tools) | hermes | 8h | 周四 | ⚪ |
| S1-009 | 集成 Agent + Toolkit + Engine | hermes | 6h | 周五 | ⚪ |
| S1-010 | 运行 20 case 测试，统计准确率 | PM | 2h | 周五 | ⚪ |
| S1-011 | Go/No-Go 决策会议 | PM | 1h | 周五 | ⚪ |

**Go 标准**: 准确率 >70%，或可通过用户确认补救到 >90%  
**No-Go 方案**: 降级为半自动 (Agent 建议 + 用户确认)  
**详细任务看板**: [`docs/PMO/sprint_1_hermes.md`](./sprint_1_hermes.md)

### hermes 本周交付物
1. AgentScope 环境 (可运行)
2. DirectorAgent 基础类 (可实例化)
3. Engine Toolkit (4 个 tools)
4. Agent + Engine 集成 (端到端流程)

---

## 9. 项目文档索引

| 文档 | 路径 | 状态 |
|------|------|------|
| 架构设计 | `docs/architecture.md` | ✅ |
| 商业计划书 | `docs/CineMate_Business_Plan_v1.0.md` | ✅ |
| 开发计划 | `docs/development_plan.md` | 🔄 (修订中) |
| API 文档 | `docs/api/` | 📝 (待创建) |
| 用户指南 | `docs/user-guide/` | 📝 (待创建) |
| 项目管理 | `docs/PMO/` | 🔄 (本目录) |

---

## 10. 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2026-04-20 | 1.0 | 初始版本 | PM |

---

> **"Plan is nothing, planning is everything."**
> — Dwight D. Eisenhower

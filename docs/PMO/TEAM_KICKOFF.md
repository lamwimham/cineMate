# CineMate 团队 Kickoff 🚀

> **Sprint 1**: 2026-04-20 ~ 2026-04-27  
> **Team**: hermes (Agent/Gateway) + copaw (Infra/Skill) + PM (AI Assistant)

---

## 👋 欢迎词

欢迎 hermes 和 copaw 加入 CineMate！

我们是一支小而精的 **2 人全栈团队**，目标是打造 AI 视频制作的 "GitHub" —— 一个由 Agent 驱动、具备版本控制和增量更新的工程化平台。

**项目愿景**: 像管理代码一样管理视频创作。

---

## 👥 团队成员

### hermes — Agent & Gateway 负责人

**你的领域**:
- Milestone 2: AgentScope 集成 (Week 1-2)
- Milestone 3: Cloud Gateway (Week 4-7)
- Milestone 5: CLI & UI (Week 9)

**本周任务**:
- Day 1: AgentScope 环境准备
- Day 2: Prompt Review + 技术设计
- Day 3: DirectorAgent 实现
- Day 4: Engine Toolkit 实现
- Day 5: 集成 + 测试 + Go/No-Go

**详细任务**: [hermes_sprint1_brief.md](./hermes_sprint1_brief.md)

---

### copaw — Infra & Skill 负责人

**你的领域**:
- Milestone 3.5: Async Infrastructure (Week 3-4)
- Milestone 4: Skill System (Week 8)
- Milestone 6: Production Readiness (Week 10-11)

**本周任务**:
- Day 1: 项目熟悉 (M1 Engine 代码)
- Day 2: Job Queue 调研 + ADR-001
- Day 3: Async 详细设计
- Day 4: Redis 环境 + JobQueue 骨架
- Day 5: 测试 + Review + 下周计划

**详细任务**: [copaw_sprint1_brief.md](./copaw_sprint1_brief.md)

---

### claude — QA & Testing 负责人 (新加入!)

**你的领域**:
- 测试框架 & CI/CD (Week 1-2)
- Quality Assurance Pipeline
- Performance Testing

**本周任务**:
- Day 1: 项目熟悉 + 测试框架搭建
- Day 2: 核心模块单元测试 (DAG, FSM, Store)
- Day 3: 集成测试 + Mock 服务
- Day 4: CI/CD + 性能测试
- Day 5: 测试报告 + Code Review + 文档

**详细任务**: [claude_sprint1_brief.md](./claude_sprint1_brief.md)

---

### PM (AI Assistant) — 项目管理 & 产品

**我的职责**:
- Sprint 规划与跟踪
- 技术决策支持
- 代码 Review
- 风险监控

---

## 🎯 Sprint 1 目标

### hermes: 验证 AgentScope Integration
**成功标准**:
- ✅ AgentScope 环境就绪
- ✅ DirectorAgent 基础类
- ✅ Engine Toolkit 4 工具
- ✅ 20 case 测试准确率 >= 70%
- ✅ Go/No-Go 决策通过

### copaw: 启动 Async Infrastructure
**成功标准**:
- ✅ 熟悉 CineMate 架构
- ✅ Async Infra 架构文档
- ✅ ADR-001 技术选型决策
- ✅ Redis 环境运行
- ✅ JobQueue 骨架实现

### claude: 建立 Testing Framework
**成功标准**:
- ✅ 测试框架搭建 (pytest + coverage)
- ✅ 核心模块单元测试 (>80% 覆盖)
- ✅ CI/CD 测试流水线
- ✅ 集成测试方案设计
- ✅ 测试报告生成

---

## 📅 本周日程

### Monday (今天) - Kickoff
| Time | Activity | Participants |
|------|----------|-------------|
| Now | Team Kickoff | All |
| 09:00 | Sprint Planning | All |
| 09:30 | 各自开始 Day 1 任务 | hermes, copaw |
| 17:00 | **Daily Standup** | All |

### Tuesday - Design & Alignment
| Time | Activity | Participants |
|------|----------|-------------|
| 09:00 | 各自继续 | hermes, copaw |
| 11:00 | **Interface Alignment Meeting** | hermes, copaw, PM |
| 14:00 | Prompt Review | hermes, PM |
| 17:00 | **Daily Standup** | All |

**会议重点**: Engine → Queue 接口定义
- 如何提交 Job?
- 如何通知完成?
- 错误处理策略?

### Wednesday - Implementation
| Time | Activity | Participants |
|------|----------|-------------|
| 09:00 | 各自开发 | hermes, copaw |
| 17:00 | **Daily Standup** | All |

### Thursday - Code & Review
| Time | Activity | Participants |
|------|----------|-------------|
| 09:00 | 各自开发 | hermes, copaw |
| 11:00 | **Code Review Prep** | copaw |
| 14:00 | **Technical Review** | All |
| 17:00 | **Daily Standup** | All |

### Friday - Integration & Decision
| Time | Activity | Participants |
|------|----------|-------------|
| 09:00 | 集成 + 测试 | hermes, copaw |
| 14:00 | 20 case 测试 | hermes, PM |
| 16:00 | **Go/No-Go Decision** | All |
| 17:00 | **Sprint Review** | All |
| 18:00 | **Retrospective** | All |

---

## 🗂️ 关键文档索引

| 文档 | 路径 | Owner |
|------|------|-------|
| 项目章程 | `docs/PMO/project_charter.md` | PM |
| Sprint 1 团队计划 | `docs/PMO/sprint_1_team.md` | PM |
| hermes 任务简报 | `docs/PMO/hermes_sprint1_brief.md` | PM |
| copaw 任务简报 | `docs/PMO/copaw_sprint1_brief.md` | PM |
| Prompt 模板 | `prompts/intent_v1.md` | PM |
| 测试用例 | `tests/test_cases_intent.json` | PM |
| 架构设计 | `docs/architecture.md` | Original |
| M1 Engine | `cine_mate/engine/` | hermes/copaw |

---

## 💬 每日 Standup

### 格式
```markdown
**Name**: hermes / copaw
**Date**: 2026-04-XX
**Yesterday**: (昨天完成了什么)
**Today**: (今天计划做什么)
**Blockers**: (有什么阻塞)
```

### 示例
```markdown
**Name**: hermes
**Date**: 2026-04-21
**Yesterday**: 安装了 AgentScope，跑通了 EchoAgent Demo
**Today**: 设计 DirectorAgent 类，Review Prompt 模板
**Blockers**: 无
```

---

## 🔧 开发工作流

### Git 分支
```
main (保护分支)
├── feature/sprint1-agent-scope (hermes)
├── feature/sprint1-async-infra (copaw)
└── feature/sprint1-testing (claude)
```

### 提交流程
```bash
# 1. 创建分支
$ git checkout -b feature/sprint1-[name]

# 2. 日常提交
$ git add .
$ git commit -m "feat(scope): description"
$ git push origin feature/sprint1-[name]

# 3. 周五创建 PR
# PM 会 Review 后合并
```

### Commit 规范
```
type(scope): description

type:
- feat: 新功能
- fix: 修复
- docs: 文档
- test: 测试
- refactor: 重构

scope:
- agents (hermes)
- tools (hermes)
- infra (copaw)
- core (shared)
```

---

## 🚨 升级机制

### 阻塞升级
遇到问题 >30 分钟无法解决？**立即 @PM**

### 决策升级
技术选型无法达成一致？**PM 仲裁**

### 时间风险
任务超过预估 50%？**立即通知 PM**

---

## 📊 本周成功检查清单

### hermes
- [ ] AgentScope 环境就绪
- [ ] DirectorAgent 可实例化
- [ ] 4 个 Toolkit tools 可用
- [ ] Agent + Toolkit + Engine 集成
- [ ] 20 case 测试完成
- [ ] Go/No-Go 决策通过

### copaw
- [ ] 熟悉 CineMate 架构
- [ ] ADR-001 决策记录
- [ ] Async Infra 架构文档
- [ ] Job Schema 定义
- [ ] Redis 环境运行
- [ ] JobQueue 骨架实现

### claude
- [ ] 测试框架搭建完成
- [ ] DAG/FSM/Store 单元测试
- [ ] 核心模块覆盖率 >80%
- [ ] CI/CD 运行成功
- [ ] 测试报告生成
- [ ] Code Review 反馈

### 团队协作
- [ ] Interface Alignment 会议完成
- [ ] 互相 Code Review
- [ ] Technical Review 完成
- [ ] Sprint Review Demo

---

## 🎉 Let's Build!

**本周金句**:
> "Alone we can do so little; together we can do so much." — Helen Keller

**有问题？** 随时 @PM

**准备好开始了吗？**
- hermes: 回复 "Day 1 开始"
- copaw: 回复 "Day 1 开始"

让我们一起打造 CineMate！🚀

---

**文档**: This is the single source of truth for Sprint 1.

**Last Updated**: 2026-04-20 by PM

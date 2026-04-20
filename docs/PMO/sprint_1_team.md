# Sprint 1: Team Plan (hermes + copaw + claude)

> **Sprint**: 1 (2026-04-20 ~ 2026-04-27)
> **Goal**:
> - hermes: Validate AgentScope Integration & NL→DAG Intent Parsing
> - copaw: Design Async Infrastructure Architecture & Kickoff Implementation
> - claude: Establish Testing Framework & Quality Assurance Pipeline
> **Team**: hermes (Agent/Gateway), copaw (Infra/Skill), claude (QA/Testing), PM (AI Assistant)

---

## 📋 团队分工

```
Week 1: Parallel Tracks
═══════════════════════════════════════════════════════════════

hermes (Agent & Gateway Track)
├── Day 1: AgentScope 环境准备
├── Day 2: Prompt Review + 技术设计
├── Day 3: DirectorAgent 实现
├── Day 4: Engine Toolkit 实现
└── Day 5: Integration + Testing
    └── Deliverable: Agent ↔ Engine 集成完成

copaw (Infra & Skill Track)
├── Day 1-2: 项目熟悉 + 架构设计
├── Day 3-4: Job Queue 设计文档
└── Day 5: 开始实现 Redis + RQ
    └── Deliverable: Async Infra 架构文档 + Job Queue 骨架

claude (QA & Testing Track)
├── Day 1: 项目熟悉 + 测试框架搭建
├── Day 2: 核心模块单元测试 (DAG, FSM, Store)
├── Day 3: 集成测试 + Mock 服务
├── Day 4: CI/CD + 性能测试
└── Day 5: 测试报告 + Code Review
    └── Deliverable: 测试框架 + 覆盖率报告

PM (协调)
├── Day 1-2: Prompt 设计 + 测试用例
├── Day 3: 支持三人技术问题
├── Day 4: Code Review 准备
└── Day 5: Go/No-Go 决策

协作点
├── Day 2: 接口对齐会议 (hermes ↔ copaw)
│   └── Topic: Engine → Async Queue 接口定义
├── Day 4: 技术 Review
│   └── Topic: 架构评审 + 代码 Review
├── Day 4: Code Review (claude 主导)
│   └── Topic: hermes & copaw 代码可测性 Review
└── Day 5: Sprint Review
    └── Topic: Demo + 决策 + Retrospective
```

---

## 🎯 Sprint 目标

### hermes 目标
**验证 AgentScope 能否与 CineMate Engine 集成**
- ✅ AgentScope 环境就绪
- ✅ DirectorAgent 基础类实现
- ✅ Engine Toolkit 4 个工具
- ✅ Agent + Toolkit + Engine 集成
- ✅ 20 个 case 测试，准确率 >= 70%

### copaw 目标
**完成 Async Infrastructure 架构设计并启动实现**
- ✅ 熟悉 CineMate 项目架构
- ✅ 完成 Async Infra 架构设计文档
- ✅ 确定 Job Queue 技术选型 (ADR-001)
- ✅ Redis + RQ 环境搭建
- ✅ Job Queue 骨架代码 (定义接口)

### claude 目标
**建立 CineMate 的测试框架和质量保障体系**
- ✅ 熟悉 CineMate 项目架构
- ✅ 测试框架搭建 (pytest + coverage)
- ✅ 为核心模块补充单元测试 (>80% 覆盖)
- ✅ 建立 CI/CD 测试流水线
- ✅ 设计集成测试方案

---

## 📅 日程安排

### Monday (Day 1) - Kickoff

| Time | Activity | Participants | Output |
|------|----------|------------|--------|
| 09:00 | Sprint Planning | All | 确认本周目标 |
| 09:30 | hermes: AgentScope 安装 | hermes | 环境就绪 |
| 09:30 | copaw: 项目架构熟悉 | copaw | 理解整体架构 |
| 12:00 | Async Check-in | All | 同步进展 |
| 14:00 | copaw: 审查 M1 Engine 代码 | copaw | 理解 DAG/FSM |
| 17:00 | **Daily Standup** | All | 阻塞同步 |

**hermes 任务**:
- [ ] S1-001: 阅读 AgentScope 文档 (2h)
- [ ] S1-002: 安装 AgentScope (1h)
- [ ] S1-003: 跑通 EchoAgent Demo (2h)
- [ ] S1-004: 查看 M1 Engine 代码 (2h)

**copaw 任务**:
- [ ] C1-001: 阅读项目文档 (2h)
- [ ] C1-002: 审查 M1 Engine 代码 (3h)
- [ ] C1-003: 理解 DAG 执行流程 (2h)

**claude 任务**:
- [ ] CL1-001: 阅读项目文档 (2h)
- [ ] CL1-002: 审查现有测试代码 (2h)
- [ ] CL1-003: 搭建测试框架 (3h)

---

### Tuesday (Day 2) - Design & Interface Alignment

| Time | Activity | Participants | Output |
|------|----------|------------|--------|
| 09:00 | hermes: 技术设计 | hermes | DirectorAgent 设计 |
| 09:00 | copaw: Async 调研 | copaw | 技术选项对比 |
| 11:00 | **Interface Alignment Meeting** | hermes, copaw, PM | 接口定义文档 |
| 14:00 | hermes: Prompt Review | hermes, PM | Prompt 反馈 |
| 14:00 | copaw: 架构设计初稿 | copaw | 架构草图 |
| 17:00 | **Daily Standup** | All | 阻塞同步 |

**hermes 任务**:
- [ ] S1-005: Review Prompt 模板 (1h)
- [ ] S1-006: 确认 DAG 结构符合 Engine (1h)
- [ ] S1-007: 设计 DirectorAgent 类 (4h)

**copaw 任务**:
- [ ] C1-004: 调研 Job Queue 方案 (3h)
- [ ] C1-005: 对比 Redis/RQ vs Celery vs 其他 (2h)
- [ ] C1-006: 撰写 ADR-001 初稿 (2h)

**Interface Alignment Meeting** (11:00, 30min):
- Topic 1: Engine 如何提交 Job 到 Queue?
  - Input: `run_id`, `node_id`, `params`
  - Output: `job_id`, `status`
- Topic 2: Queue 如何通知 Engine 完成?
  - Option A: Callback URL
  - Option B: Status polling
  - Decision: ???
- Topic 3: 错误处理策略

**产出**: `docs/architecture/async_interface.md`

---

### Wednesday (Day 3) - Implementation Start

| Time | Activity | Participants | Output |
|------|----------|------------|--------|
| 09:00 | hermes: DirectorAgent 实现 | hermes | 基础类完成 |
| 09:00 | copaw: Job Queue 详细设计 | copaw | 详细设计文档 |
| 14:00 | copaw: Redis 环境搭建 | copaw | Redis 运行 |
| 17:00 | **Daily Standup** | All | 阻塞同步 |

**hermes 任务**:
- [ ] S1-008: 创建 `cine_mate/agents/__init__.py` (0.5h)
- [ ] S1-009: 实现 `director_agent.py` (6h)
- [ ] S1-010: 单元测试 (1h)

**copaw 任务**:
- [ ] C1-007: Job Queue 详细设计 (4h)
- [ ] C1-008: Redis + RQ 安装配置 (2h)
- [ ] C1-009: 编写 Job Schema (2h)

**产出**:
- hermes: `cine_mate/agents/director_agent.py`
- copaw: `docs/architecture/job_queue_design.md`

---

### Thursday (Day 4) - Toolkit & Queue Skeleton

| Time | Activity | Participants | Output |
|------|----------|------------|--------|
| 09:00 | hermes: Engine Toolkit 实现 | hermes | 4 个 tools |
| 09:00 | copaw: Job Queue 骨架 | copaw | 基础接口 |
| 11:00 | **Code Review Prep** | copaw | Review hermes 代码 |
| 14:00 | **Technical Review** | All | 架构评审 |
| 17:00 | **Daily Standup** | All | 阻塞同步 |

**hermes 任务**:
- [ ] S1-011: 创建 `tools/engine_tools.py` (0.5h)
- [ ] S1-012: 实现 `create_pipeline_tool` (3h)
- [ ] S1-013: 实现 `get_run_status_tool` (2h)
- [ ] S1-014: 实现 `modify_node_tool` (2h)
- [ ] S1-015: 实现 `list_runs_tool` (1h)

**copaw 任务**:
- [ ] C1-010: 实现 `JobQueue` 类 (4h)
- [ ] C1-011: 实现 `submit_job()` 方法 (2h)
- [ ] C1-012: 实现 `get_job_status()` 方法 (2h)
- [ ] C1-013: Code Review hermes PR (1h)

**Technical Review** (14:00, 1h):
- hermes 展示: DirectorAgent + Toolkit 设计
- copaw 展示: Job Queue 架构
- 讨论: 集成点 + 风险
- 决策: 是否需要调整

---

### Friday (Day 5) - Integration & Review

| Time | Activity | Participants | Output |
|------|----------|------------|--------|
| 09:00 | hermes: Agent + Toolkit + Engine 集成 | hermes | 集成完成 |
| 09:00 | copaw: Job Queue 测试 + 文档 | copaw | 单元测试 |
| 14:00 | hermes: 20 case 测试 | hermes, PM | 测试报告 |
| 16:00 | **Go/No-Go Decision** | All | 决策记录 |
| 17:00 | **Sprint Review** | All | Demo |
| 18:00 | **Retrospective** | All | 改进点 |

**hermes 任务**:
- [ ] S1-016: Agent + Toolkit + Engine 集成 (3h)
- [ ] S1-017: 运行 20 case 测试 (2h)
- [ ] S1-018: 修复发现的问题 (2h)
- [ ] S1-019: 准备 Demo (1h)

**copaw 任务**:
- [ ] C1-014: Job Queue 单元测试 (3h)
- [ ] C1-015: 编写文档 (2h)
- [ ] C1-016: Code Review hermes PR (1h)
- [ ] C1-017: 准备下周计划 (1h)

**Sprint Review** (17:00, 1h):
- hermes Demo: Agent → Toolkit → Engine 流程
- copaw Demo: Job Queue 提交/查询
- PM: 测试报告 + 准确率统计
- Decision: Go/No-Go

**Retrospective** (18:00, 30min):
- What went well?
- What could be improved?
- Action items for next sprint

---

## 📁 代码规范

### 分支策略
```
main (保护分支)
├── feature/sprint1-agent-scope (hermes)
├── feature/sprint1-async-infra (copaw)
└── feature/sprint1-testing (claude)
```

### Git Workflow
```bash
# hermes
$ git checkout -b feature/sprint1-agent-scope
$ git commit -m "feat(agents): add DirectorAgent skeleton"
$ git push origin feature/sprint1-agent-scope
# 周五创建 PR

# copaw
$ git checkout -b feature/sprint1-async-infra
$ git commit -m "feat(infra): add JobQueue skeleton"
$ git push origin feature/sprint1-async-infra
# 周五创建 PR

# claude
$ git checkout -b feature/sprint1-testing
$ git commit -m "test(dag): add comprehensive DAG tests"
$ git push origin feature/sprint1-testing
# 周五创建 PR
```

### Code Review 流程
1. **Self Review**: 提交前自己检查
2. **Peer Review**:
   - hermes 的代码 → copaw Review (功能), claude Review (可测性)
   - copaw 的代码 → hermes Review (接口), claude Review (可测性)
   - claude 的代码 → hermes Review (集成), copaw Review (性能)
3. **PM Review**: PM 最终审批
4. **Merge**: PM 合并到 main

---

## 💬 每日 Standup

### 格式
```markdown
**Name**: hermes / copaw / claude
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

## 🚧 风险与应对

| Risk ID | Description | Owner | Mitigation |
|---------|-------------|-------|------------|
| S1-R1 | NL→DAG 准确率不足 | hermes/PM | 周五 Go/No-Go，准备降级方案 |
| S1-R2 | AgentScope 依赖冲突 | hermes | Day 1 解决，实在不行换方案 |
| S1-R3 | Async 设计复杂度过高 | copaw | Day 2 接口对齐会议简化 |
| S1-R4 | 两人进度不匹配 | PM | 每日 Standup 跟踪，必要时调整 |
| S1-R5 | Redis 环境搭建失败 | copaw | 使用 Docker，备选 SQLite Queue |
| S1-R6 | 测试框架配置问题 | claude | Day 1 解决，备选 unittest |
| S1-R7 | 模块依赖复杂难以 Mock | claude/hermes | 简化接口，使用依赖注入 |
| S1-R8 | 三人进度协调 | PM | 每日 Standup，必要时调整 |

---

## ✅ 验收标准

### hermes 验收
- [ ] AgentScope 安装成功
- [ ] DirectorAgent 可实例化
- [ ] 4 个 Toolkit tools 可用
- [ ] Agent → Toolkit → Engine 流程跑通
- [ ] 20 case 测试完成
- [ ] Go/No-Go 决策通过

### copaw 验收
- [ ] 熟悉 CineMate 架构
- [ ] Async Infra 架构文档完成
- [ ] ADR-001 决策记录
- [ ] Redis 环境运行
- [ ] JobQueue 骨架实现
- [ ] 基础接口定义文档

### claude 验收
- [ ] 测试框架搭建完成
- [ ] DAG/FSM/Store 单元测试 (>80% 覆盖)
- [ ] CI/CD 测试流水线运行
- [ ] 集成测试方案设计
- [ ] 测试报告生成
- [ ] Code Review 反馈

---

## 📚 参考文档

| 文档 | 路径 | Owner |
|------|------|-------|
| AgentScope Docs | https://doc.agentscope.io/ | hermes |
| Prompt 模板 | `prompts/intent_v1.md` | PM |
| 测试用例 | `tests/test_cases_intent.json` | PM |
| M1 Engine | `cine_mate/engine/` | hermes |
| Async 设计 | `docs/architecture/async_interface.md` | copaw |
| Job Queue 设计 | `docs/architecture/job_queue_design.md` | copaw |

---

**Prepared by**: PM (AI Assistant)  
**For**: hermes & copaw  
**Date**: 2026-04-20

> **"Alone we can do so little; together we can do so much."** — Helen Keller

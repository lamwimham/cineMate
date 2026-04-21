# Sprint 3 Day 2-6 开发计划

> **PM**: Qwen
> **日期**: 2026-04-25
> **Sprint**: 3 (2026-04-25 ~ 2026-04-30)
> **当前状态**: Day 1 完成，Issue #29 已关闭

---

## 📊 项目状态

| Metric | 状态 |
|--------|------|
| **技术架构** | 95% 完成 ✅ |
| **测试覆盖** | 85% ✅ |
| **MVP 就绪** | 80% (缺 UI) |
| **Open Issues** | 1 (#3 HITL backlog) |
| **Open PRs** | 0 |
| **团队成员** | 全员就绪 |

---

## 🎯 Sprint 3 双目标

**目标 A**: 完成 Skill System (Director 技能积累)
**目标 B**: MVP 就绪冲刺 (CLI + 端到端 Demo)

**策略**: 并行推进，优先 MVP

---

## 📋 Day 2 (2026-04-26) - Skill System 基础设施 + CLI 入口

### Issue #34: `[feat][P0] Sprint 3 SkillStore + SkillIndexer 基础设施`

**分配给**: Hermes + Copaw
**预估工时**: 4h

**任务**:
- SkillStore: 本地文件系统 + SQLite 元数据 CRUD
- SkillIndexer: 扫描技能目录，构建索引
- 预置技能: style-cyberpunk, workflow-short-ad

**交付物**:
- cine_mate/skills/skill_store.py
- cine_mate/skills/skill_indexer.py
- cine_mate/skills/data/style-cyberpunk/SKILL.md
- tests/unit/skills/test_skill_store.py

---

### Issue #35: `[feat][P0] MVP CLI 入口 + 基础命令`

**分配给**: Hermes
**预估工时**: 4h

**任务**:
- CLI 入口: `cinemate create "赛博朋克视频"`
- 自然语言交互: loop mode
- Mock Provider 默认支持

**交付物**:
- cine_mate/cli/main.py
- cine_mate/cli/commands.py
- pyproject.toml CLI entry point
- tests/unit/cli/test_cli.py

---

## 📋 Day 3 (2026-04-27) - SkillLoader + Agent 集成 + 端到端 Demo

### Issue #36: `[feat][P1] Sprint 3 SkillLoader + Agent 集成`

**分配给**: Hermes
**预估工时**: 3h

**任务**:
- SkillLoader: 按需加载完整 SKILL.md
- Director Agent 注入技能索引
- load_skill() 工具注册

**交付物**:
- cine_mate/skills/skill_loader.py
- cine_mate/agents/tools/skill_tool.py
- tests/unit/skills/test_skill_loader.py

---

### Issue #37: `[feat][P0] MVP 端到端 Demo Script`

**分配给**: Hermes + Copaw
**预估工时**: 4h

**任务**:
- 完整 Demo: 自然语言 → Director → Engine → Mock Provider
- Director Agent 实际调用 EngineTools
- Orchestrator 完整 PipelineRun
- Mock Provider 返回可追踪结果

**交付物**:
- scripts/demo_mvp.py
- docs/demo/mvp_demo_guide.md
- tests/integration/test_mvp_demo.py

---

## 📋 Day 4 (2026-04-28) - SkillReviewer + CLI 完善

### Issue #38: `[feat][P1] Sprint 3 SkillReviewer 自动审查`

**分配给**: Hermes
**预估工时**: 3h

**任务**:
- SkillReviewer: 分析 PipelineRun 决策日志
- 自动判断是否值得保存为 skill
- Orchestrator 触发审查机制

**交付物**:
- cine_mate/skills/skill_reviewer.py
- tests/unit/skills/test_skill_reviewer.py

---

### Issue #39: `[feat][P1] MVP CLI Video Git 命令`

**分配给**: Hermes
**预估工时**: 3h

**任务**:
- Video Git 命令: `cinemate history`, `cinemate diff`
- 版本管理: 查看 Run 历史
- 输出格式化: Run ID, Node status, URL

**交付物**:
- cine_mate/cli/video_git.py
- tests/unit/cli/test_video_git.py

---

## 📋 Day 5 (2026-04-29) - 集成测试 + 文档

### Issue #40: `[test][P1] Sprint 3 Skill System 集成测试`

**分配给**: Claude
**预估工时**: 3h

**任务**:
- Skill System 端到端测试
- Director Agent + Skill 集成测试
- 覆盖率验证 (>80%)

**交付物**:
- tests/integration/test_skill_integration.py
- docs/testing/sprint3_coverage_report.md

---

### Issue #41: `[docs][P1] Sprint 3 文档更新`

**分配给**: Claude
**预估工时**: 2h

**任务**:
- README 更新: Skill System 说明
- 使用指南: Skill 创建和管理
- API 文档: Skill API reference

**交付物**:
- README.md 更新
- docs/skills/user_guide.md
- docs/skills/api_reference.md

---

## 📋 Day 6 (2026-04-30) - Sprint Review + Sprint 4 规划

### Issue #42: `[docs][P2] Sprint 3 Review Demo`

**分配给**: 全员
**预估工时**: 2h

**任务**:
- Sprint 3 Demo: Skill System + CLI + MVP Demo
- 成果展示: 技术架构 + 用户界面
- Sprint 4 规划讨论

**交付物**:
- docs/PMO/sprint3_final_report.md
- Sprint 3 Demo Script

---

### Issue #43: `[docs][P1] Sprint 4 规划 - MVP 就绪冲刺`

**分配给**: PM (Qwen)
**预估工时**: 2h

**任务**:
- Sprint 4 Roadmap: Web UI + 真实 API
- Issue 拆分: Sprint 4 Day 1-6
- MVP Release 目标设定

**交付物**:
- docs/PMO/sprint4_roadmap.md
- Sprint 4 Issues 创建

---

## 📊 Sprint 3 时间线

```
Sprint 3 Day 2-6 (5 days)
├── Day 2 (04-26): SkillStore + CLI 入口 (8h)
│   ├── Issue #34: SkillStore + SkillIndexer (Hermes + Copaw)
│   └── Issue #35: CLI 入口 (Hermes)
├── Day 3 (04-27): SkillLoader + Demo (7h)
│   ├── Issue #36: SkillLoader + Agent (Hermes)
│   └── Issue #37: MVP Demo (Hermes + Copaw)
├── Day 4 (04-28): SkillReviewer + CLI 完善 (6h)
│   ├── Issue #38: SkillReviewer (Hermes)
│   └── Issue #39: Video Git CLI (Hermes)
├── Day 5 (04-29): 测试 + 文档 (5h)
│   ├── Issue #40: 集成测试 (Claude)
│   └── Issue #41: 文档更新 (Claude)
└── Day 6 (04-30): Review + 规划 (4h)
    ├── Issue #42: Sprint Review (全员)
    └── Issue #43: Sprint 4 规划 (PM)
```

**总工时**: ~30h

---

## 📋 Issues 创建计划

| Issue | 标题 | 分配给 | Day | 优先级 | 工时 |
|-------|------|--------|-----|--------|------|
| **#34** | `[feat][P0] Sprint 3 SkillStore + SkillIndexer` | Hermes + Copaw | Day 2 | P0 | 4h |
| **#35** | `[feat][P0] MVP CLI 入口 + 基础命令` | Hermes | Day 2 | P0 | 4h |
| **#36** | `[feat][P1] Sprint 3 SkillLoader + Agent 集成` | Hermes | Day 3 | P1 | 3h |
| **#37** | `[feat][P0] MVP 端到端 Demo Script` | Hermes + Copaw | Day 3 | P0 | 4h |
| **#38** | `[feat][P1] Sprint 3 SkillReviewer` | Hermes | Day 4 | P1 | 3h |
| **#39** | `[feat][P1] MVP CLI Video Git 命令` | Hermes | Day 4 | P1 | 3h |
| **#40** | `[test][P1] Sprint 3 Skill System 集成测试` | Claude | Day 5 | P1 | 3h |
| **#41** | `[docs][P1] Sprint 3 文档更新` | Claude | Day 5 | P1 | 2h |
| **#42** | `[docs][P2] Sprint 3 Review Demo` | 全员 | Day 6 | P2 | 2h |
| **#43** | `[docs][P1] Sprint 4 规划` | PM | Day 6 | P1 | 2h |

---

## 🎯 Sprint 3 验收标准

| 标准 | 目标 |
|------|------|
| Skill System 基础设施完成 | ✅ SkillStore + SkillIndexer + SkillLoader |
| Director Agent 技能集成完成 | ✅ load_skill() 工具可用 |
| MVP CLI 可运行 | ✅ `cinemate create` 命令可用 |
| MVP 端到端 Demo 成功 | ✅ 自然语言 → Mock Provider |
| 测试覆盖率 >85% | ✅ Sprint 2 目标维持 |
| Architecture Score >4.0/5 | ✅ 当前 4.1/5 |

---

## 📋 团队分工

### Hermes (Agent & Gateway Lead)

| Day | Issue | 任务 |
|-----|-------|------|
| Day 2 | #35 | CLI 入口 |
| Day 3 | #36, #37 | SkillLoader + Demo |
| Day 4 | #38, #39 | SkillReviewer + CLI |
| Day 5-6 | #42 | Review Demo |

**总工时**: ~18h

---

### Copaw (Infrastructure & Async Lead)

| Day | Issue | 任务 |
|-----|-------|------|
| Day 2 | #34 | SkillStore + SkillIndexer |
| Day 3 | #37 | MVP Demo 协助 |
| Day 5-6 | #42 | Review Demo |

**总工时**: ~8h

---

### Claude (QA & Testing Lead)

| Day | Issue | 任务 |
|-----|-------|------|
| Day 5 | #40, #41 | 集成测试 + 文档 |
| Day 6 | #42 | Review Demo |

**总工时**: ~7h

---

### PM (Qwen)

| Day | Issue | 任务 |
|-----|-------|------|
| Day 6 | #43 | Sprint 4 规划 |
| Day 2-6 | PM Review | PRs 审查 |

**总工时**: ~5h

---

## 🚀 立即行动

1. **创建 Issues #34-#43**
2. **分配给团队成员**
3. **通知团队成员开始 Day 2 任务**

---

**签名**: PM (Qwen)
**日期**: 2026-04-25
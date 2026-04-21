# CineMate Sprint 3 Roadmap: 导演 Agent 技能系统

> **To**: PM (AI Assistant)
> **From**: hermes
> **Date**: 2026-04-24
> **Status**: 待审阅

---

## 🎯 Sprint 3 主题：导演 Agent 技能系统 (Director Skill System)

**核心目标**：为 DirectorAgent 构建基于**渐进式披露**的 Skill 系统，让 Agent 在视频制作过程中积累经验、复用风格策略、自动恢复错误。

**设计哲学**：借鉴 OpenCode 渐进式披露机制，采用 `目录索引 → 按需加载` 模式，而非全量注入 system prompt。

---

## 📋 阶段划分

### Phase 1: 基础设施 (Sprint 3 Day 1-2, 约 8h)

| 任务 | 工作量 | 交付物 | 说明 |
|------|--------|--------|------|
| **SkillStore** | 3h | `cine_mate/skills/skill_store.py` | 本地文件系统 + SQLite 元数据存储。支持 create/read/update/delete。YAML frontmatter 验证。 |
| **SkillIndexer** | 2h | `cine_mate/skills/skill_indexer.py` | 扫描技能目录，构建索引。提供 `available()` 方法返回 name + description 列表。支持按场景过滤。 |
| **SkillLoader** | 2h | `cine_mate/skills/skill_loader.py` | 按需加载完整 SKILL.md 内容 + 文件列表。返回 `<skill_content>` 格式字符串。 |
| **预置技能** | 1h | 3 个 SKILL.md 模板 | `style-cyberpunk`、`workflow-short-ad`、`error-kling-face` |

**验收标准**：
- [ ] SkillStore 支持 CRUD 操作
- [ ] SkillIndexer 正确扫描并缓存索引
- [ ] SkillLoader 按需加载完整内容
- [ ] 预置技能可被正确发现和加载

---

### Phase 2: Agent 集成 (Sprint 3 Day 3-4, 约 8h)

| 任务 | 工作量 | 交付物 | 说明 |
|------|--------|--------|------|
| **System Prompt 注入** | 1h | `director_agent.py` 修改 | 在 system prompt 中注入技能索引（仅 name + description）。参考 OpenCode `Skill.fmt()` 格式。 |
| **Skill 工具** | 2h | `cine_mate/agents/tools/skill_tool.py` | 提供 `load_skill(name)` 工具。注册到 DirectorAgent Toolkit。返回 `<skill_content>` 格式。 |
| **技能触发引导** | 1h | System Prompt 增强 | "When you recognize a task matches an available skill, use load_skill to load it." |
| **多轮迭代支持** | 2h | `orchestrator.py` 修改 | PipelineRun 结束时，将当前 run 的决策日志传递给 Reviewer。 |
| **测试验证** | 2h | 集成测试 | Mock Agent 调用 load_skill，验证技能内容正确注入。 |

**验收标准**：
- [ ] DirectorAgent 启动时加载技能索引
- [ ] Agent 可调用 load_skill 加载完整技能
- [ ] 技能内容在对话历史中持续可用
- [ ] 集成测试通过

---

### Phase 3: 自动审查与经验沉淀 (Sprint 3 Day 5-6, 约 8h)

| 任务 | 工作量 | 交付物 | 说明 |
|------|--------|--------|------|
| **SkillReviewer** | 3h | `cine_mate/skills/skill_reviewer.py` | PipelineRun 结束后触发。分析本次 run 的决策日志，判断是否值得保存为 skill。 |
| **触发机制** | 1h | `orchestrator.py` 修改 | 每次 PipelineRun 完成（成功/失败/重试），自动触发 Reviewer。 |
| **审查 Prompt** | 1h | 预置审查 prompt | "Review this run: was a non-trivial style choice made? Was an error recovered? If so, save as skill." |
| **技能创建集成** | 2h | DirectorAgent 集成 | Reviewer 调用 SkillStore.create() 保存新技能。 |
| **技能更新机制** | 1h | SkillStore.update() | 当发现已有技能需要更新时（如新的错误恢复方式），自动 patch。 |

**验收标准**：
- [ ] PipelineRun 结束自动触发审查
- [ ] Reviewer 可识别可复用经验
- [ ] 自动创建/更新技能
- [ ] 审查结果通知用户

---

### Phase 4: 高级特性 (Sprint 4, 约 6h)

| 任务 | 工作量 | 交付物 | 说明 |
|------|--------|--------|------|
| **技能分类** | 1h | SkillStore 扩展 | 支持 `style/`, `workflow/`, `error-recovery/` 分类。按场景过滤。 |
| **技能权限** | 1h | 配置系统扩展 | 不同 Agent/用户可访问不同技能集合。 |
| **远程技能** | 2h | `skill_discovery.py` | 支持从 URL 拉取技能集合（类似 OpenCode `index.json` 机制）。 |
| **技能市场** | 2h | 文档 + CLI | 提供 `hermes skills install <url>` 命令。 |

---

## 📊 总体时间线

```
Sprint 3 (6 days, ~24h)
├── Day 1-2: Phase 1 - 基础设施 (8h)
│   ├── SkillStore, SkillIndexer, SkillLoader
│   └── 预置技能
├── Day 3-4: Phase 2 - Agent 集成 (8h)
│   ├── System Prompt 注入, Skill 工具
│   └── 测试验证
└── Day 5-6: Phase 3 - 自动审查 (8h)
    ├── SkillReviewer, 触发机制
    └── 技能创建/更新集成

Sprint 4 (2 days, ~6h)
├── Day 1: 技能分类 + 权限
└── Day 2: 远程技能 + 技能市场
```

---

## 📁 预期文件结构

```
cine_mate/
├── agents/
│   ├── director_agent.py          # 修改：注入技能索引 + 注册 skill 工具
│   └── tools/
│       ├── engine_tools.py        # 现有
│       └── skill_tool.py          # 新增：load_skill(name)
├── skills/                        # 新增：技能系统核心
│   ├── __init__.py
│   ├── skill_store.py             # CRUD + 元数据
│   ├── skill_indexer.py           # 扫描 + 缓存 + available()
│   ├── skill_loader.py            # 按需加载完整内容
│   ├── skill_reviewer.py          # 自动审查逻辑
│   └── data/                      # 实际技能文件
│       ├── style-cyberpunk/
│       │   └── SKILL.md
│       ├── workflow-short-ad/
│       │   └── SKILL.md
│       └── error-kling-face/
│           └── SKILL.md
└── engine/
    └── orchestrator.py            # 修改：触发审查 + 传递决策日志
```

---

## ⚠️ 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| LLM 不主动调用 load_skill | 技能系统失效 | System Prompt 强化引导 + 测试验证 |
| 审查产生低质量技能 | 技能库污染 | 审查 Prompt 优化 + 人工审核开关 |
| 技能内容过大导致上下文溢出 | Agent 性能下降 | 技能内容上限 10K chars + 分段加载 |
| 多 Agent 并发修改技能 | 数据竞争 | 文件锁 + SQLite 事务 |

---

**备注**：具体任务拆分、优先级排序和时间安排以 PM 最终决策为准。本文档仅供技术参考。

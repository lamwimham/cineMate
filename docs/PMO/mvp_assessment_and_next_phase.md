# CineMate MVP 评估与下一阶段规划

> **PM**: Qwen
> **日期**: 2026-04-25
> **当前 Sprint**: Sprint 3 Day 1 完成

---

## 📊 MVP 评估

### MVP 定义

**CineMate MVP** 应能让用户：
1. **自然语言输入** → Director Agent 解析意图
2. **DAG 构建** → Engine 规划视频生成流程
3. **Provider 调用** → 生成实际视频（或 Mock 模式）
4. **增量修改** → 脏传播重新渲染变更节点
5. **版本管理** → Video Git 历史追踪

---

## ✅ 已完成的 MVP 组件

| 组件 | 模块 | 状态 | 验证 |
|------|------|------|------|
| **DAG Engine** | `engine/dag.py` | ✅ 完成 | 42 tests, 100% coverage |
| **FSM** | `engine/fsm.py` | ✅ 完成 | 42 tests, 97% coverage |
| **Orchestrator** | `engine/orchestrator.py` | ✅ 完成 | 事件驱动 |
| **Store** | `core/store.py` | ✅ 完成 | 35 tests, 100% coverage |
| **JobQueue** | `infra/queue.py` | ✅ 完成 | Redis-backed |
| **EventBus** | `infra/event_bus.py` | ✅ 完成 | 21 tests, 71% coverage |
| **Worker** | `infra/worker.py` | ✅ 完成 | RQ workers |
| **Provider Factory** | `adapters/factory.py` | ✅ 完成 | Kling/Runway/Mock |
| **Base Provider** | `adapters/base.py` | ✅ 完成 | 53 tests, 86% coverage |
| **Director Agent** | `agents/director_agent.py` | ✅ 完成 | AgentScope 集成 |
| **Config System** | `config/` | ✅ 完成 | 多模式配置 |
| **CI/CD** | `.github/workflows/` | ✅ 完成 | GitHub Actions |

**架构完整度**: ✅ **95%**

---

## ⏳ 缺失的 MVP 组件

| 组件 | 说明 | 优先级 | 影响 |
|------|------|--------|------|
| **用户界面** | 无 CLI/Web UI | 🔴 **P0** | 用户无法交互 |
| **端到端 Demo** | 自然语言 → 视频完整流程未验证 | 🔴 **P0** | MVP 无法演示 |
| **HITL** | Human-in-the-Loop 节点审批 | 🟡 **P1** | Issue #3 backlog |
| **Skill System** | Director 技能积累 | 🟡 **P1** | Sprint 3 规划中 |
| **真实 API 验证** | Kling/Runway 真实调用未测试 | 🟡 **P1** | Mock 模式仅验证架构 |

---

## 🎯 MVP 就绪评估

### 结论：**未就绪 (80% 完成)**

**核心问题**：
1. 🔴 **缺少用户界面**：最大 MVP 缺陷
2. 🔴 **端到端流程未打通**：无完整 Demo 验证
3. 🟡 **真实 API 未验证**：仅 Mock Provider 测试

**技术架构就绪**：✅ 是
**用户体验就绪**：❌ 否

---

## 📋 Sprint 3 剩余任务 (Day 2-6)

| Day | 任务 | 负责人 | 预估工时 |
|-----|------|--------|----------|
| Day 2 | SkillStore + SkillIndexer | Hermes + Copaw | 5h |
| Day 3 | SkillLoader + Agent 集成 | Hermes | 4h |
| Day 4 | SkillReviewer + 自动审查 | Hermes | 4h |
| Day 5 | 集成测试 + Sprint Review | Claude | 3h |
| Day 6 | Sprint 4 规划 | PM | 2h |

---

## 🚀 Sprint 4 规划建议：MVP 就绪冲刺

### Sprint 4 主题：MVP 用户界面 + 端到端验证

**目标**：让用户能真正使用 CineMate

---

### Phase 1: CLI 接口 (Day 1-2, 8h)

| 任务 | 交付物 | 说明 |
|------|--------|------|
| **CLI 入口** | `cine_mate/cli/main.py` | `cinemate create "赛博朋克视频"` |
| **自然语言交互** | CLI loop mode | 持续对话修改视频 |
| **Video Git 命令** | `cinemate history`, `cinemate diff` | 版本管理 |
| **输出展示** | CLI 格式化输出 | Run ID, Node status, URL |

**验收标准**：
- [ ] 用户可通过 CLI 创建视频任务
- [ ] CLI 支持自然语言输入
- [ ] CLI 支持查看历史和版本差异
- [ ] Mock 模式下完整 Demo 可运行

---

### Phase 2: 端到端 Demo (Day 3, 6h)

| 任务 | 交付物 | 说明 |
|------|--------|------|
| **完整 Demo Script** | `scripts/demo_mvp.py` | 自然语言 → Mock Provider → 辆辆结果 |
| **Director Agent 验证** | Agent 实际调用 EngineTools | 真实 DAG 构建 |
| **Orchestrator 验证** | 完整 PipelineRun 执行 | FSM 状态流转 |
| **Mock Provider 集成** | Mock 生成可追踪结果 | URL 模拟 |

**验收标准**：
- [ ] Demo Script 运行成功
- [ ] Director Agent 正确解析意图
- [ ] DAG 正确构建和执行
- [ ] Mock Provider 返回结果

---

### Phase 3: Web UI (Day 4-5, 10h) [可选]

| 任务 | 交付物 | 说明 |
|------|--------|------|
| **FastAPI 后端** | `cine_mate/api/` | REST API + WebSocket |
| **简单 Web 界面** | `frontend/` | React/Vue 视频管理界面 |
| **视频预览** | URL 展示 | Mock URL 演示 |

**验收标准**：
- [ ] 用户可通过 Web UI 创建任务
- [ ] WebSocket 实时显示进度
- [ ] 视频结果可预览（Mock URL）

---

### Phase 4: 真实 API 验证 (Day 6, 4h)

| 任务 | 交付物 | 说明 |
|------|--------|------|
| **Kling API 测试** | 测试脚本 | 真实 text_to_video |
| **Runway API 测试** | 测试脚本 | 真实 image_to_video |
| **API Key 管理** | CLI/API 配置 | 多 Provider API Key |

**验收标准**：
- [ ] 真实 Kling/Runway 调用成功
- [ ] API Key 安全存储
- [ ] 生成真实视频 URL

---

## 📊 Sprint 4 时间线

```
Sprint 4 (6 days, ~28h)
├── Day 1-2: Phase 1 - CLI 接口 (8h)
│   ├── CLI 入口, 自然语言交互
│   └── Video Git 命令
├── Day 3: Phase 2 - 端到端 Demo (6h)
│   ├── Demo Script, Director 验证
│   └── Orchestrator + Mock Provider 验证
├── Day 4-5: Phase 3 - Web UI (10h) [可选]
│   ├── FastAPI 后端
│   └── 简单 Web 界面
└── Day 6: Phase 4 - 真实 API 验证 (4h)
    ├── Kling/Runway API 测试
    └── API Key 管理
```

---

## 🎯 MVP 就绪里程碑

| Milestone | Sprint | 目标 | 验收标准 |
|-----------|--------|------|----------|
| **M1: 技术架构** | Sprint 1-3 | ✅ 已完成 | 所有模块测试通过 |
| **M2: MVP Demo** | Sprint 4 Phase 2 | ⏳ 待完成 | 端到端 Demo 可运行 |
| **M3: MVP CLI** | Sprint 4 Phase 1 | ⏳ 待完成 | CLI 可交互使用 |
| **M4: MVP Web** | Sprint 4 Phase 3 | ⏳ 可选 | Web UI 可访问 |
| **M5: MVP Release** | Sprint 5 | 📋 规划中 | 真实 API + 生产部署 |

---

## ⚠️ 风险与建议

### 风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| **无用户界面** | 🔴 MVP 无法交付 | Sprint 4 Phase 1 优先 |
| **端到端未验证** | 🔴 架构可能存在集成问题 | Sprint 4 Phase 2 Demo |
| **真实 API 未测试** | 🟡 Provider 可能无法工作 | Sprint 4 Phase 4 测试 |
| **Skill System 复杂** | 🟡 可能延期 | Sprint 3 完成基础，Sprint 4+ 完善 |

### 建议

1. **优先级调整**：
   - Sprint 4 Phase 1 (CLI) + Phase 2 (Demo) **最高优先级**
   - Phase 3 (Web UI) 可延至 Sprint 5
   - Phase 4 (真实 API) 可与 Phase 1-2 并行

2. **MVP 范围**：
   - **最小 MVP**：CLI + Mock Provider + 端到端 Demo
   - **完整 MVP**：CLI + Web UI + 真实 API

3. **时间预估**：
   - Sprint 4 MVP Demo + CLI：约 14h（2-3 days）
   - Sprint 4 Web UI + 真实 API：约 14h（可选延至 Sprint 5）

---

## 📋 立即行动

### Sprint 3 Day 2 任务

| Issue | 标题 | 负责人 | 优先级 |
|-------|------|--------|--------|
| 新 Issue | `[feat][P0] Sprint 3 SkillStore + SkillIndexer` | Hermes + Copaw | P0 |
| 新 Issue | `[feat][P1] Sprint 3 SkillLoader + Agent 集成` | Hermes | P1 |
| 新 Issue | `[test][P1] Sprint 3 Skill System 集成测试` | Claude | P1 |

### Sprint 4 规划 Issue

| Issue | 标题 | Sprint | 优先级 |
|-------|------|--------|--------|
| 新 Issue | `[feat][P0] Sprint 4 CLI 接口 + MVP Demo` | Sprint 4 | P0 |

---

## 🎯 PM 决策

### Sprint 3 继续 Skill System

- ✅ Sprint 3 Roadmap 已批准
- ✅ Skill System 是 Director Agent 的重要增强
- ⏳ 继续按 Sprint 3 Roadmap 执行

### Sprint 4 MVP 就绪冲刺

- 📋 **最高优先级**：CLI + 端到端 Demo
- 📋 **次要优先级**：Web UI + 真实 API
- 📋 **目标**：Sprint 4 结束时 MVP Demo 可运行

---

## 📊 项目健康度

| 维度 | 评分 | 说明 |
|------|------|------|
| **技术架构** | ⭐⭐⭐⭐⭐ 5/5 | 全部模块完成 |
| **测试覆盖** | ⭐⭐⭐⭐⭐ 85% | Sprint 2 目标达成 |
| **文档完整性** | ⭐⭐⭐⭐⭐ 5/5 | PMO docs 完整 |
| **用户可用性** | ⭐⭐ 2/5 | **缺少 UI** |
| **MVP 就绪** | ⭐⭐⭐⭐ 4/5 | 80% 完成 |

---

**签名**: PM (Qwen)
**日期**: 2026-04-25
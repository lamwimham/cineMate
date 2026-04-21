# Sprint 4 规划 — MVP 就绪冲刺

> **PM**: Qwen  
> **日期**: 2026-04-21  
> **Sprint**: Sprint 4 (Day 1-6)  
> **目标**: MVP Release

---

## 🎯 Sprint 4 目标

**主题**: MVP 就绪冲刺 — 让用户能真正使用 CineMate

**核心目标**:
1. ✅ CLI 接口 (Sprint 3 已完成 #35, #39)
2. 🔜 Web UI 可视化界面
3. 🔜 真实 API 验证 (Kling/Runway)
4. 🔜 MVP Release 准备

---

## 📊 Sprint 3 完成状态

| 组件 | 状态 | PR | 测试 |
|------|------|-----|------|
| SkillStore + SkillIndexer | ✅ Merged | #43 | 29/29 |
| CLI Entry Point | ✅ Merged | #44 | 25/25 |
| SkillLoader + DirectorAgent | ✅ Merged | #46 | 14/14 |
| MVP E2E Demo | ✅ Merged | #45 | 8/8 |
| SkillReviewer Auto-generation | ✅ Merged | #47 | 15/15 |
| Video Git CLI | ✅ Merged | #48 | 21/21 |
| Documentation Update | ✅ Merged | commit | - |

**Sprint 3 完成度**: 7/7 P1 ✅

---

## 📋 Sprint 4 Issue 拆分

### Issue #44: Web UI Backend (P1)

**标题**: `[feat][P1] Sprint 4 Web UI Backend`

**负责人**: Hermes

**任务**:
- FastAPI 后端 REST API
- WebSocket 实时进度推送
- 视频任务 CRUD API
- Run 状态查询 API

**交付物**:
- `cine_mate/api/main.py`: FastAPI 应用
- `cine_mate/api/routes/`: REST API 路由
- `cine_mate/api/schemas.py`: API 数据模型

**验收标准**:
- [ ] REST API 可创建视频任务
- [ ] WebSocket 推送节点进度
- [ ] API 文档 (OpenAPI/Swagger)

**预估工时**: 5h

---

### Issue #45: Web UI Frontend (P1)

**标题**: `[feat][P1] Sprint 4 Web UI Frontend`

**负责人**: Hermes

**任务**:
- React/Vue 前端界面
- 视频 Git 可视化
- Run 历史展示
- 实时进度显示

**交付物**:
- `frontend/src/`: React/Vue 源码
- 视频任务创建表单
- Run 详情页面
- Video Git timeline 视图

**验收标准**:
- [ ] 用户可通过 Web UI 创建任务
- [ ] 实时进度 WebSocket 连接
- [ ] Run 历史可浏览

**预估工时**: 6h

---

### Issue #46: Real API Validation (P1)

**标题**: `[test][P1] Sprint 4 真实 API 验证`

**负责人**: Copaw + Claude

**任务**:
- Kling API 真实调用测试
- Runway API 真实调用测试
- API Key 配置管理
- Provider 错误处理验证

**交付物**:
- `tests/integration/test_kling_real.py`: Kling 真实 API 测试
- `tests/integration/test_runway_real.py`: Runway 真实 API 测试
- API Key 配置文档

**验收标准**:
- [ ] Kling text_to_video 真实调用成功
- [ ] Runway image_to_video 真实调用成功
- [ ] API Key 安全存储
- [ ] 生成真实视频 URL

**预估工时**: 4h

---

### Issue #47: MVP Release Preparation (P1)

**标题**: `[docs][P1] Sprint 4 MVP Release 准备`

**负责人**: PM + Claude

**任务**:
- MVP Release Checklist
- 生产环境配置
- 用户文档更新
- Demo 视频录制

**交付物**:
- MVP Release Checklist 文档
- 用户手册 `docs/user_manual.md`
- Demo 视频/GIF

**验收标准**:
- [ ] MVP Release Checklist 完成
- [ ] 用户手册可用
- [ ] Demo 视频可展示

**预估工时**: 3h

---

### Issue #48: Sprint 4 Integration Test (P1)

**标题**: `[test][P1] Sprint 4 集成测试`

**负责人**: Claude

**任务**:
- Web UI + API 集成测试
- E2E 用户流程测试
- 性能测试
- 错误恢复测试

**交付物**:
- `tests/integration/test_web_api.py`: Web API 集成测试
- `tests/integration/test_e2e_user_flow.py`: 用户流程测试

**验收标准**:
- [ ] Web API 集成测试通过
- [ ] E2E 用户流程测试通过

**预估工时**: 3h

---

### Issue #49: Sprint 5 Planning (P1)

**标题**: `[docs][P1] Sprint 5 规划`

**负责人**: PM

**任务**:
- Sprint 5 Roadmap
- MVP 后续增强规划
- HITL (Issue #3) 评估

**交付物**:
- `docs/PMO/sprint5_roadmap.md`
- Issue #3 HITL 规划

**验收标准**:
- [ ] Sprint 5 Roadmap 完成
- [ ] HITL 规划完成

**预估工时**: 2h

---

## 📅 Sprint 4 时间线

```
Sprint 4 (6 days, ~23h)
├── Day 1-2: Issue #44 + #45 (Web UI)
│   ├── Backend: FastAPI + WebSocket (5h)
│   └── Frontend: React/Vue 界面 (6h)
├── Day 3: Issue #46 (Real API Validation)
│   ├── Kling + Runway 真实测试 (4h)
├── Day 4: Issue #47 + #48 (MVP Prep + Integration)
│   ├── Release 准备 + 用户文档 (3h)
│   └── 集成测试 (3h)
├── Day 5: Sprint Review + Demo
│   └── MVP Demo 展示
└── Day 6: Issue #49 (Sprint 5 Planning)
    └── Sprint 5 Roadmap (2h)
```

---

## 👥 团队分工

### Hermes (Agent & Gateway Lead)

| Day | Issue | 任务 |
|-----|-------|------|
| Day 1-2 | #44, #45 | Web UI Backend + Frontend |
| Day 5 | - | MVP Demo 协助 |

**总工时**: ~11h

---

### Copaw (Infra & Async Lead)

| Day | Issue | 任务 |
|-----|-------|------|
| Day 3 | #46 | Real API Validation (Kling/Runway) |
| Day 5 | - | MVP Demo 协助 |

**总工时**: ~4h

---

### Claude (QA & Testing Lead)

| Day | Issue | 任务 |
|-----|-------|------|
| Day 3 | #46 | Real API 测试协助 |
| Day 4 | #48 | 集成测试 |
| Day 5 | - | Review Demo |

**总工时**: ~5h

---

### PM (Qwen)

| Day | Issue | 任务 |
|-----|-------|------|
| Day 4 | #47 | MVP Release 准备 |
| Day 6 | #49 | Sprint 5 规划 |
| Day 1-6 | PM Review | PRs 审查 |

**总工时**: ~5h

---

## 🎯 MVP Release Milestones

| Milestone | Sprint | 状态 | 验收标准 |
|-----------|--------|------|----------|
| **M1: 技术架构** | Sprint 1-3 | ✅ 完成 | 所有模块测试通过 |
| **M2: MVP CLI** | Sprint 3 | ✅ 完成 | CLI 可交互使用 |
| **M3: MVP Demo** | Sprint 3 | ✅ 完成 | 端到端 Demo 可运行 |
| **M4: Web UI** | Sprint 4 | ⏳ 待完成 | Web UI 可访问 |
| **M5: Real API** | Sprint 4 | ⏳ 待完成 | 真实视频生成 |
| **M6: MVP Release** | Sprint 4 | ⏳ 待完成 | MVP Release Checklist |

---

## ⚠️ 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Web UI 时间不足 | 🟡 | 可简化 UI，延至 Sprint 5 |
| API Key 配置复杂 | 🟡 | 优先 CLI 配置，Web UI 后续 |
| Kling/Runway API 问题 | 🟡 | Mock Provider 作为备选 |

---

## 🚀 立即行动

1. **创建 Issues #44-#49**
2. **分配给团队成员**
3. **通知团队开始 Sprint 4**

---

**签名**: PM (Qwen)  
**日期**: 2026-04-21
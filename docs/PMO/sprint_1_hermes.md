# Sprint 1: AgentScope Spike - hermes 任务看板

> **Sprint**: 1 (2026-04-20 ~ 2026-04-27)  
> **Goal**: Validate NL→DAG Intent Parsing Viability  
> **Developer**: hermes  
> **PM**: AI Assistant

---

## 🎯 Sprint 目标

**验证 AgentScope 能否将自然语言准确转换为 DAG 工作流**

成功标准:
- ✅ 安装 AgentScope 并跑通基础 Demo
- ✅ 实现最小可行 Intent Parser
- ✅ 20 个测试 case 准确率 >= 70%
- ✅ 通过 Go/No-Go 决策

---

## 📋 任务列表

### Day 1 (周一) - 环境准备

| 任务 ID | 任务 | 预估工时 | 优先级 | 验收标准 | 状态 |
|---------|------|----------|--------|----------|------|
| S1-001 | 阅读 AgentScope 官方文档 | 2h | Must | 理解 ReActAgent 概念 | 🟡 |
| S1-002 | 安装 AgentScope: `pip install agentscope` | 1h | Must | 安装成功，无冲突 | ⚪ |
| S1-003 | 跑通官方 EchoAgent Demo | 2h | Must | 能运行并看到输出 | ⚪ |
| S1-004 | 查看 M1 引擎代码，理解 DAG 结构 | 2h | Must | 能画出 M1 DAG 类图 | ⚪ |
| S1-005 | **Daily Standup** | 15min | - | 同步今日进展 | ⚪ |

**Day 1 Deliverable**: 
- [ ] AgentScope 环境就绪
- [ ] 本地可运行 EchoAgent

---

### Day 2 (周二) - Prompt 设计

| 任务 ID | 任务 | 预估工时 | 优先级 | 验收标准 | 状态 |
|---------|------|----------|--------|----------|------|
| S1-006 | 设计 Intent → DAG 的 Prompt 模板 v1 | 4h | Must | 覆盖 3 种场景 | ⚪ |
| S1-007 | 准备 20 个测试 case (NL 描述) | 2h | Must | 覆盖简单/中等/复杂 | ⚪ |
| S1-008 | 手动测试 Prompt (用 ChatGPT/Claude) | 2h | Should | 记录准确率 | ⚪ |
| S1-009 | **Daily Standup** | 15min | - | 同步今日进展 | ⚪ |

**Prompt 场景覆盖**:
1. **简单**: "生成一个赛博朋克风格的短视频"
2. **中等**: "创建一个 10 秒的产品展示视频，先展示产品全貌，然后特写功能"
3. **复杂**: "制作一个王家卫风格的短片，包含慢动作、霓虹灯、帧内帧构图"

**Day 2 Deliverable**:
- [ ] `prompts/intent_v1.md` 文件
- [ ] `tests/test_cases_intent.json` (20 个 case)
- [ ] 手动测试结果记录

---

### Day 3 (周三) - DirectorAgent 骨架

| 任务 ID | 任务 | 预估工时 | 优先级 | 验收标准 | 状态 |
|---------|------|----------|--------|----------|------|
| S1-010 | 创建 `cine_mate/agents/__init__.py` | 1h | Must | 模块初始化 | ⚪ |
| S1-011 | 实现 `DirectorAgent` 基础类 | 4h | Must | 继承 ReActAgent | ⚪ |
| S1-012 | 编写 System Prompt | 2h | Must | 包含角色定义、工具说明 | ⚪ |
| S1-013 | **Daily Standup** | 15min | - | 同步今日进展 | ⚪ |

**Day 3 Deliverable**:
- [ ] `cine_mate/agents/director_agent.py` (骨架)
- [ ] 可实例化，响应基础指令

---

### Day 4 (周四) - Engine Toolkit

| 任务 ID | 任务 | 预估工时 | 优先级 | 验收标准 | 状态 |
|---------|------|----------|--------|----------|------|
| S1-014 | 设计 Engine Toolkit 接口 | 2h | Must | 4 个核心 tool | ⚪ |
| S1-015 | 实现 `create_pipeline_tool` | 3h | Must | 能创建 Run | ⚪ |
| S1-016 | 实现 `get_run_status_tool` | 2h | Must | 能查询状态 | ⚪ |
| S1-017 | **Daily Standup** | 15min | - | 同步今日进展 | ⚪ |

**Toolkit 接口**:
```python
class EngineToolkit(Toolkit):
    def create_pipeline(prompt: str) -> str: ...  # return run_id
    def get_run_status(run_id: str) -> dict: ...
    def modify_node(run_id: str, node_id: str, params: dict) -> bool: ...
    def list_runs() -> list: ...
```

**Day 4 Deliverable**:
- [ ] `cine_mate/agents/tools/engine_tools.py`
- [ ] Toolkit 可注册到 DirectorAgent

---

### Day 5 (周五) - 集成测试 & Go/No-Go

| 任务 ID | 任务 | 预估工时 | 优先级 | 验收标准 | 状态 |
|---------|------|----------|--------|----------|------|
| S1-018 | 集成 Agent + Toolkit + M1 Engine | 3h | Must | 端到端流程跑通 | ⚪ |
| S1-019 | 运行 20 个 case，统计准确率 | 2h | Must | 输出测试报告 | ⚪ |
| S1-020 | 编写 Sprint 1 总结文档 | 2h | Should | 记录经验教训 | ⚪ |
| S1-021 | **Go/No-Go 决策会议** | 1h | Must | 决策记录 | ⚪ |
| S1-022 | **Sprint Review** | 1h | - | Demo + 反馈 | ⚪ |
| S1-023 | **Retrospective** | 30min | - | 改进点 | ⚪ |

**Go/No-Go 标准**:
- ✅ Go: 准确率 >= 70%，或可通过用户确认补救到 >= 90%
- ❌ No-Go: 准确率 < 50%，需降级为半自动模式

**Day 5 Deliverable**:
- [ ] 20 case 测试报告
- [ ] Go/No-Go 决策记录
- [ ] Sprint 1 回顾文档

---

## 📊 工作量统计

| 日期 | 预估工时 | 实际工时 | 完成任务数 |
|------|----------|----------|------------|
| 周一 | 7h | - | - |
| 周二 | 8h | - | - |
| 周三 | 7h | - | - |
| 周四 | 7h | - | - |
| 周五 | 8.5h | - | - |
| **总计** | **37.5h** | - | **23 个任务** |

---

## 🚧 阻塞与风险

| 风险 ID | 描述 | 概率 | 应对方案 |
|---------|------|------|----------|
| R-S1-001 | AgentScope 安装依赖冲突 | 中 | 用虚拟环境隔离 |
| R-S1-002 | NL→DAG 准确率过低 | 高 | 提前准备 No-Go 方案 |
| R-S1-003 | M1 Engine 接口不理解 | 低 | PM 提供代码讲解 |

---

## 💬 每日 Standup 模板

hermes 请在每天结束时回复以下格式:

```markdown
**Date**: 2026-04-XX
**Yesterday**: (昨天完成了什么)
**Today**: (今天计划做什么)
**Blockers**: (有什么阻塞，没有就写 "None")
```

---

## 📁 代码提交规范

### 分支策略
```
main (保护分支)
  └── feature/sprint1-agent-scope (hermes 工作分支)
```

### Commit Message 格式
```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `test`: 测试
- `refactor`: 重构

**Examples**:
```
feat(agents): add DirectorAgent skeleton

feat(tools): implement create_pipeline_tool

test(agents): add 20 intent parsing test cases
```

### PR 流程
1. hermes 完成开发 → 创建 PR → 指派 PM
2. PM Code Review → 提出修改意见
3. hermes 修改 → PM Approve
4. PM Merge to main

---

## 📚 参考资料

| 文档 | 路径 | 说明 |
|------|------|------|
| AgentScope Docs | https://doc.agentscope.io/ | 官方文档 |
| M1 Engine Code | `cine_mate/engine/` | 需要集成的引擎 |
| Prompt Template | `prompts/intent_v1.md` (待创建) | Prompt 设计 |
| Test Cases | `tests/test_cases_intent.json` (待创建) | 测试数据 |

---

## ✅ Sprint 1 完成检查清单

- [ ] AgentScope 安装成功
- [ ] DirectorAgent 基础类实现
- [ ] Engine Toolkit 4 个工具实现
- [ ] 20 个测试 case 准备
- [ ] 准确率测试报告
- [ ] Go/No-Go 决策完成
- [ ] 代码 Review 通过
- [ ] 文档已更新

---

**Prepared by**: PM (AI Assistant)  
**For**: hermes  
**Date**: 2026-04-20

> **"The best way to predict the future is to implement it."** — David Heinemeier Hansson

# hermes - Day 5 任务通知

> **日期**: 2026-04-21 (Day 5)
> **状态**: ✅ Sprint 1 集成测试已通过 (PR #9)
> **优先级**: P0/P1 任务，今日完成

---

## 🎉 Day 4 成果确认

**PR #9 已合并，Engine → Queue → Worker 异步流程跑通！**

你的贡献:
- DirectorAgent 实现完成
- Engine Toolkit 4 个工具可用
- 与 copaw 完成集成联调

---

## 📋 Day 5 任务清单

### P0 任务 (必须完成)

#### 1. Agent + Toolkit + Engine 最终集成测试 (预估 2h)

**测试目标**: 验证完整流程 Agent → Toolkit → Engine → Queue → Worker

**测试脚本**:
```python
# tests/integration/test_agent_full_flow.py
import asyncio
from cine_mate.agents.director_agent import DirectorAgent
from cine_mate.infra.queue import JobQueue
from cine_mate.infra.event_bus import EventBus

async def test_full_flow():
    """完整流程集成测试"""
    # 1. 初始化 Agent
    agent = DirectorAgent(name="Director")

    # 2. 用户输入自然语言
    result = await agent.chat(
        "创建一个 5 秒的赛博朋克城市视频，霓虹灯效果"
    )

    # 3. 验证 Agent 响应
    assert result.run_id is not None
    assert result.status in ["queued", "running", "completed"]

    # 4. 查询状态
    status = await agent.tools.get_run_status(result.run_id)
    assert "progress" in status

    print(f"✅ Full Flow Test Passed: {result.run_id}")

asyncio.run(test_full_flow())
```

---

#### 2. 20 个 Case 测试执行 (预估 2h)

**测试用例来源**: `tests/test_cases_intent.json` 或 PM 提供

**测试维度**:
| 维度 | 测试内容 | 示例 |
|------|----------|------|
| 基础生成 | 单节点生成 | "生成一张赛博朋克图片" |
| 链式生成 | Script → Image → Video | "创建一个短视频，主题是日落" |
| 风格指定 | 带风格参数 | "用王家卫风格拍一段雨夜街景" |
| 参数调整 | 修改已有节点 | "把第 2 个镜头改成慢动作" |
| 版本回溯 | 基于 parent_run | "基于上次结果，换一种色调" |

**准确率目标**: >= 70%

**测试报告格式**:
```markdown
## NL→DAG 测试报告

| Case ID | 输入 | 预期 DAG | 实际 DAG | 匹配度 | 状态 |
|---------|------|----------|----------|--------|------|
| 001 | "赛博朋克视频" | 3 nodes | 3 nodes | 100% | ✅ |
| 002 | "王家卫风格雨夜" | style param | style param | 90% | ✅ |
| ... | ... | ... | ... | ... | ... |

**总体准确率**: X%
**通过/总数**: Y/20
```

---

#### 3. 准备 Sprint Review Demo (预估 1h)

**Demo 内容** (与 PM 协调):

```python
# demo_script.py
"""
Sprint 1 Demo: Agent → Engine → Queue 全流程展示

演示步骤:
1. 用户输入自然语言
2. Agent 解析意图，生成 DAG
3. DAG 提交到 Engine
4. Engine 创建 Job 发送到 Queue
5. Worker 执行 Job
6. 状态更新，返回结果
"""

import asyncio
from cine_mate.agents.director_agent import DirectorAgent

async def demo():
    print("🎬 === CineMate Sprint 1 Demo ===")
    print()

    # 初始化
    agent = DirectorAgent(name="Director")
    print("✅ DirectorAgent 初始化完成")

    # 用户输入
    user_input = "创建一个 5 秒的赛博朋克城市视频，霓虹灯光效"
    print(f"📝 用户输入: {user_input}")

    # Agent 处理
    result = await agent.chat(user_input)
    print(f"🤖 Agent 响应:")
    print(f"   - run_id: {result.run_id}")
    print(f"   - DAG nodes: {result.dag_nodes}")
    print(f"   - status: {result.status}")

    # 等待执行
    print("⏳ 等待 Worker 执行...")
    await asyncio.sleep(10)

    # 查询最终状态
    final_status = await agent.tools.get_run_status(result.run_id)
    print(f"✅ 最终状态: {final_status}")

    print()
    print("🎉 Demo 完成!")

asyncio.run(demo())
```

---

### P1 任务 (争取完成)

#### 4. 补充 Agent 单元测试 (预估 1h)

创建测试文件:
```
tests/unit/agents/
├── __init__.py
├── test_director_agent.py
└── test_engine_tools.py
```

**test_director_agent.py 测试用例**:
```python
@pytest.mark.asyncio
async def test_agent_initialization():
    """Agent 初始化测试"""
    agent = DirectorAgent(name="Director")
    assert agent.name == "Director"
    assert agent.tools is not None

@pytest.mark.asyncio
async def test_agent_chat_basic():
    """基础对话测试"""
    agent = DirectorAgent()
    result = await agent.chat("创建一个视频")
    assert result is not None

@pytest.mark.asyncio
async def test_intent_to_dag():
    """意图解析测试"""
    agent = DirectorAgent()
    dag = await agent.parse_intent("赛博朋克风格")
    assert "nodes" in dag
```

---

#### 5. Code Review copaw 代码 (预估 0.5h)

**审查重点**:
| 模块 | 审查项 | 关注点 |
|------|--------|--------|
| `queue.py` | JobQueue 接口 | 是否与 Engine Toolkit 正确对接 |
| `event_bus.py` | EventBus 事件 | 事件格式是否符合约定 |
| `worker.py` | Worker 执行 | 是否正确处理 Job 回调 |

**Review 输出格式**:
```markdown
## Code Review: copaw Sprint 1 Infra 代码

### 整体评价
[优秀/良好/需改进]

### 接口对接检查
| 接口 | 状态 | 备注 |
|------|------|------|
| JobQueue.submit_job | ✅ | 参数正确传递 |
| JobQueue.get_job_status | ✅ | 返回格式符合 |
| EventBus.publish | ✅ | schema 正确 |

### 建议
1. ...
2. ...
```

---

### P2 任务 (时间允许)

#### 6. 优化 Prompt 模板 (预估 1h)

根据 20 case 测试结果，优化 `prompts/intent_v1.md`:
- 补充常见错误案例
- 添加边界情况处理
- 优化 DAG 生成规则

---

## 📅 今日时间表

| 时间 | 任务 | 状态 |
|------|------|------|
| 09:00 - 11:00 | Agent + Toolkit + Engine 集成测试 | ⏳ |
| 11:00 - 13:00 | 20 Case 测试执行 | ⏳ |
| 13:00 - 14:00 | Demo 准备 | ⏳ |
| 14:00 - 14:30 | Code Review copaw | ⏳ |
| 14:30 - 15:30 | 补充 Agent 单元测试 | ⏳ |
| 16:00 | Go/No-Go 决策 | ⏳ |
| 17:00 | Sprint Review Demo | ⏳ |

---

## ✅ 验收标准

**Day 5 完成标志**:
- [ ] Agent + Toolkit + Engine + Queue 全流程跑通
- [ ] 20 Case 测试完成，准确率 >= 70%
- [ ] Demo 可正常演示
- [ ] 单元测试覆盖率 >80%
- [ ] Code Review copaw 反馈已提交
- [ ] Go/No-Go 决策通过

---

## 🎯 Go/No-Go 决策标准

**Go Criteria** (满足即可继续):
- ✅ NL→DAG 准确率 >= 70%
- ✅ 或 "Agent 建议 + 用户确认" 模式可达 >= 90%

**No-Go Fallback** (备选方案):
- ❌ 准确率 < 50%，降级为半自动模式
- ❌ Agent 仅提供表单建议，用户手动确认

---

## 🚨 阻塞升级

如有以下情况，立即反馈:
- Agent 无法正确解析意图
- Toolkit 与 Engine 接口不一致
- Queue 返回格式不匹配
- 20 case 准确率低于预期
- Demo 无法正常运行

---

## 📞 Standup 回复格式

**Day 5 结束时请回复**:
```markdown
**Name**: hermes
**Date**: 2026-04-21 (Day 5)
**Yesterday**: PR #9 合并，集成测试通过
**Today**: 最终集成测试 + 20 Case 测试 + Demo
**Blockers**: [如有阻塞请填写]
```

---

**开始执行！Sprint 1 的最后冲刺！** 🚀

---

**Prepared by**: PM (AI Assistant)
**For**: hermes
**Date**: 2026-04-21
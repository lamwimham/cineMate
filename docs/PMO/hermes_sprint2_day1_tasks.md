# hermes Sprint 2 Day 1 任务通知

> **To**: hermes (Agent/Gateway 负责人)
> **From**: PM (AI Assistant)
> **Date**: 2026-04-22 (Sprint 2 Day 1)
> **Priority**: P0

---

## 📋 Day 1 任务清单

### 任务 1: 修复 5 个 P0 问题 (预计 6h)

**来源**: `docs/review/code_review_hermes_agents.md` (copaw Code Review)

| # | 问题 | 文件 | 修复方案 |
|---|------|------|----------|
| 1 | DirectorAgent 硬编码 DashScopeChatModel | `agents/director_agent.py` | 依赖注入 model 参数 |
| 2 | EngineTools 直接实例化 Store | `agents/tools/engine_tools.py` | 依赖注入 store 参数 |
| 3 | EngineTools 未使用 JobQueue | `agents/tools/engine_tools.py` | 集成 JobQueue.submit_job() |
| 4 | Orchestrator 未发布完成事件 | `engine/orchestrator.py` | 添加 event_bus.publish() |
| 5 | Orchestrator 未订阅事件 | `engine/orchestrator.py` | 添加 event_bus.subscribe() |

---

### 任务 2: Issue #4 Mock Mode 修复 (预计 2h)

**Issue**: https://github.com/lamwimham/cineMate/issues/4

**问题**: `director_agent.py:79` 抛出 NotImplementedError，无 API Key 环境无法测试

**修复方案**:
```python
# director_agent.py
class DirectorAgent:
    def __init__(self, model=None, model_name: str = "qwen-max", mock_mode: bool = False, ...):
        if mock_mode:
            self.model = MockChatModel()  # 不需要 API Key
        elif model:
            self.model = model
        else:
            self.model = DashScopeChatModel(...)
```

---

## 🔧 修复代码示例

### 修复 1: DirectorAgent 依赖注入

```python
# agents/director_agent.py
from typing import Optional
from agentscope.models import ChatModel

class DirectorAgent:
    def __init__(
        self,
        model: Optional[ChatModel] = None,
        model_name: str = "qwen-max",
        mock_mode: bool = False,
        **kwargs
    ):
        if mock_mode:
            self.model = self._create_mock_model()
        elif model is not None:
            self.model = model
        else:
            self.model = DashScopeChatModel(
                model_name=model_name,
                api_key=os.getenv("DASHSCOPE_API_KEY"),
            )
```

---

### 修复 2: EngineTools 依赖注入

```python
# agents/tools/engine_tools.py
from typing import Optional
from cine_mate.infra.store import Store
from cine_mate.infra.queue import JobQueue

class EngineTools:
    def __init__(
        self,
        store: Optional[Store] = None,
        job_queue: Optional[JobQueue] = None,
        store_path: str = "./cinemate.db",
    ):
        self.store = store or Store(store_path)
        self.job_queue = job_queue
```

---

### 修复 3: EngineTools JobQueue 集成

```python
# agents/tools/engine_tools.py
async def create_video(self, prompt: str, ...) -> ToolResponse:
    run = PipelineRun(...)
    await self.store.create_run(run)

    # 使用 JobQueue 提交任务
    if self.job_queue:
        job_id = await self.job_queue.submit_job(
            run_id=run.run_id,
            node_id="intent_parse",
            job_type=JobType.TEXT_TO_VIDEO,
            params={"prompt": prompt}
        )
        return ToolResponse(
            success=True,
            data={"run_id": run.run_id, "job_id": job_id}
        )
```

---

### 修复 4: Orchestrator 事件发布

```python
# engine/orchestrator.py
async def _execute_node(self, node_id: str):
    try:
        result = await self.executor_fn(node_id, self.config)

        # 发布完成事件
        if self.event_bus:
            await self.event_bus.publish(
                NodeCompletedEvent(
                    run_id=self.run.run_id,
                    node_id=node_id,
                    payload={"result": result}
                )
            )
    except Exception as e:
        if self.event_bus:
            await self.event_bus.publish(
                NodeFailedEvent(
                    run_id=self.run.run_id,
                    node_id=node_id,
                    error=str(e)
                )
            )
```

---

### 修复 5: Orchestrator 事件订阅

```python
# engine/orchestrator.py
async def start_event_driven_mode(self):
    """启动事件驱动模式"""
    if self.event_bus:
        self.event_bus.subscribe("node_completed", self._on_node_completed)
        self.event_bus.subscribe("node_failed", self._on_node_failed)
        await self.event_bus.start_listening()

async def _on_node_completed(self, event: NodeCompletedEvent):
    """事件回调：节点完成后触发下游"""
    self.completed_nodes.add(event.node_id)

    children = list(self.dag.graph.successors(event.node_id))
    for child_id in children:
        parents = list(self.dag.graph.predecessors(child_id))
        if all(p in self.completed_nodes for p in parents):
            await self._submit_node(child_id)
```

---

## ✅ 验收标准

- [ ] DirectorAgent 支持依赖注入 (model 参数)
- [ ] DirectorAgent 支持 mock_mode (无 API Key 可测试)
- [ ] EngineTools 支持依赖注入 (store + job_queue 参数)
- [ ] EngineTools 使用 JobQueue.submit_job() 提交任务
- [ ] Orchestrator 发布 NodeCompletedEvent / NodeFailedEvent
- [ ] Orchestrator 订阅 node_completed / node_failed 事件
- [ ] Issue #4 关闭 (Mock Mode 可测试)
- [ ] 单元测试通过

---

## 📝 提交要求

### PR 格式

```
Title: fix(agents): P0 issues - dependency injection + JobQueue integration

Body:
- Fix DirectorAgent hardcoded DashScopeChatModel (P0 #1)
- Fix EngineTools direct Store instantiation (P0 #2)
- Fix EngineTools JobQueue integration (P0 #3)
- Fix Orchestrator event publishing (P0 #4)
- Fix Orchestrator event subscription (P0 #5)
- Fix Issue #4 Mock Mode NotImplementedError

Closes #4
Refs: docs/review/code_review_hermes_agents.md
```

---

## ⏰ 时间安排

| 时间 | 任务 |
|------|------|
| 09:30 - 12:00 | 修复 P0 #1-#3 (DirectorAgent + EngineTools) |
| 14:00 - 16:00 | 修复 P0 #4-#5 (Orchestrator 事件) |
| 16:00 - 17:00 | Issue #4 Mock Mode 修复 |
| 17:00 | Daily Standup |

---

## 📞 协作

- **11:00**: 接口对齐会议 (与 copaw 对齐 JobQueue/EventBus 接口)
- **Standup**: 17:00 汇报进度

---

**签名**: PM (AI Assistant)
**日期**: 2026-04-22
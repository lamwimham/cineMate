# Code Review - hermes Agent 代码

> **Reviewer**: copaw (Infra & Skill 负责人)  
> **审查日期**: 2026-04-21 14:45  
> **审查范围**: DirectorAgent + EngineTools + Orchestrator  
> **Sprint**: 1

---

## 📋 审查对象

1. `cine_mate/agents/director_agent.py` - Director Agent (ReActAgent)
2. `cine_mate/agents/tools/engine_tools.py` - Engine 工具集
3. `cine_mate/engine/orchestrator.py` - 编排器 (Event-Driven)

---

## ✅ 优点

### 1. 架构设计

- ✅ **清晰的职责分离**: DirectorAgent 负责意图解析，EngineTools 负责引擎交互，Orchestrator 负责编排
- ✅ **符合 Event-Driven 架构**: Orchestrator 实现了 `_on_node_completed()` 事件回调
- ✅ **异步兼容**: 所有关键方法都是 `async def`，与 Async Infra 对齐

### 2. 代码质量

- ✅ **类型注解**: 关键函数有完整的类型提示
- ✅ **文档字符串**: 类和方法都有详细的 docstring
- ✅ **错误处理**: 有基本的 try/except 和错误返回

### 3. Event-Driven 实现

```python
# orchestrator.py - 事件回调机制
async def _on_node_completed(self, event: NodeCompletedEvent):
    """事件回调：节点完成后触发下游"""
    self.completed_nodes.add(event.node_id)
    
    # 找到下游节点
    children = list(self.dag.graph.successors(event.node_id))
    for child_id in children:
        # 检查所有父节点是否完成
        parents = list(self.dag.graph.predecessors(child_id))
        if all(p in self.completed_nodes for p in parents):
            await self._submit_node(child_id)
```

✅ **符合会议决议**: Event-Driven 回调机制（非轮询）

---

## ⚠️ 改进建议

### 1. 可测试性 (P0)

#### 问题 1: DirectorAgent 硬编码依赖

**代码**:
```python
# director_agent.py
def __init__(self, model_name: str = "qwen-max", ...):
    model = DashScopeChatModel(...)  # 硬编码具体实现
```

**问题**: 难以单元测试，依赖外部 API

**建议**: 注入模型实例
```python
def __init__(self, model=None, model_name: str = "qwen-max", ...):
    if model is None:
        model = DashScopeChatModel(...)
    self.model = model
```

**优先级**: 🔴 P0

---

#### 问题 2: EngineTools 缺少依赖注入

**代码**:
```python
# engine_tools.py
class EngineTools:
    def __init__(self, store_path: str = "./cinemate.db"):
        self.store = Store(store_path)  # 直接实例化
```

**问题**: 测试时无法 Mock Store

**建议**:
```python
class EngineTools:
    def __init__(self, store: Optional[Store] = None, store_path: str = "./cinemate.db"):
        self.store = store or Store(store_path)
```

**优先级**: 🔴 P0

---

#### 问题 3: Orchestrator 缺少事件总线集成测试

**代码**:
```python
# orchestrator.py
def __init__(self, ..., event_bus: Optional[Any] = None):
    self.event_bus = event_bus
```

**观察**: 有 `event_bus` 参数但未看到订阅逻辑

**建议**: 添加事件订阅方法
```python
async def start_event_driven_mode(self):
    """启动事件驱动模式"""
    if self.event_bus:
        self.event_bus.subscribe("node_completed", self._on_node_completed)
        await self.event_bus.start_listening()
```

**优先级**: 🟡 P1

---

### 2. 错误处理 (P1)

#### 问题 4: 缺少重试机制

**代码**:
```python
# engine_tools.py
async def create_video(self, prompt: str, ...) -> ToolResponse:
    run = PipelineRun(...)
    await self.store.create_run(run)  # 无重试
```

**建议**: 添加重试逻辑
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
async def create_video(self, prompt: str, ...):
    ...
```

**优先级**: 🟡 P1

---

#### 问题 5: 异常信息不够详细

**代码**:
```python
# director_agent.py
except Exception as e:
    print(f"Warning: Could not load prompt file. Using fallback. Error: {e}")
```

**建议**: 记录完整堆栈
```python
import traceback
except Exception as e:
    traceback.print_exc()
    print(f"Warning: Could not load prompt file: {e}")
```

**优先级**: 🟡 P1

---

### 3. Event-Driven 对齐 (P0)

#### 问题 6: EventBus 未与 JobQueue 集成

**观察**: 
- `EngineTools.create_video()` 直接调用 Store
- 未通过 JobQueue 提交任务
- 与 Sprint 1 Infra 不兼容

**建议**: 更新工具以使用 JobQueue
```python
# engine_tools.py
from cine_mate.infra.queue import JobQueue
from cine_mate.infra.schemas import JobType

class EngineTools:
    def __init__(self, ..., job_queue: Optional[JobQueue] = None):
        self.job_queue = job_queue
    
    async def create_video(self, prompt: str, ...):
        # 提交到 JobQueue 而非直接执行
        job_id = await self.job_queue.submit_job(
            run_id=run_id,
            node_id="intent_parse",
            job_type=JobType.TEXT_TO_VIDEO,
            params={"prompt": prompt}
        )
```

**优先级**: 🔴 P0 (与 Sprint 1 Infra 集成关键)

---

#### 问题 7: 事件发布未使用 EventBus

**代码**:
```python
# orchestrator.py
async def _on_node_completed(self, event: NodeCompletedEvent):
    # 只处理事件，未发布事件
```

**建议**: 完成时发布事件
```python
async def _execute_node(self, node_id: str):
    try:
        result = await self.executor_fn(node_id, config)
        
        # 发布完成事件
        if self.event_bus:
            await self.event_bus.publish(NodeCompletedEvent(
                run_id=self.run.run_id,
                node_id=node_id,
                payload={"result": result}
            ))
    except Exception as e:
        # 发布失败事件
        if self.event_bus:
            await self.event_bus.publish(NodeFailedEvent(...))
```

**优先级**: 🔴 P0

---

### 4. 代码风格 (P2)

#### 问题 8: 混合中英文注释

**观察**: 代码中混合使用中英文注释
```python
# 事件回调：节点完成后触发下游 (参考文档方案)
# Find downstream nodes
```

**建议**: 统一为英文（或中文），保持团队一致性

**优先级**: 🟢 P2

---

#### 问题 9: 缺少日志级别

**代码**:
```python
print(f"🎧 [Event] Received node_completed for {event.node_id}")
```

**建议**: 使用 logging 模块
```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"Received node_completed for {event.node_id}")
```

**优先级**: 🟢 P2

---

## 📊 审查总结

| 类别 | 问题数 | P0 | P1 | P2 |
|------|--------|----|----|----|
| 可测试性 | 3 | 3 | 0 | 0 |
| 错误处理 | 2 | 0 | 2 | 0 |
| Event-Driven | 2 | 2 | 0 | 0 |
| 代码风格 | 2 | 0 | 0 | 2 |
| **总计** | **9** | **5** | **2** | **2** |

---

## 🎯 关键行动项

### P0 - 必须修复（影响 Sprint 1 集成）

1. **DirectorAgent 依赖注入** - 使模型可 Mock
2. **EngineTools 依赖注入** - 使 Store 可 Mock
3. **JobQueue 集成** - EngineTools 使用 JobQueue 提交任务
4. **事件发布** - Orchestrator 完成时发布事件
5. **事件订阅** - Orchestrator 订阅 EventBus

### P1 - 应该修复（改进质量）

6. **重试机制** - 添加网络/DB 重试
7. **异常日志** - 记录完整堆栈

### P2 - 可以修复（代码风格）

8. **注释统一** - 统一中英文
9. **日志模块** - 使用 logging 替代 print

---

## ✅ 与 Sprint 1 Infra 的对齐检查

| 接口 | 状态 | 备注 |
|------|------|------|
| Event Schema v1.0 | ✅ | 使用 `NodeCompletedEvent` |
| JobQueue 接口 | ❌ | 需更新 EngineTools |
| EventBus 集成 | ❌ | 需添加订阅/发布 |
| Event-Driven 回调 | ✅ | `_on_node_completed()` 已实现 |
| 异步兼容 | ✅ | 所有方法都是 async |

---

## 📝 后续步骤

1. **hermes**: 修复 P0 问题（依赖注入 + JobQueue 集成）
2. **copaw**: 提供 JobQueue/EventBus 使用示例
3. **联合测试**: 验证 DirectorAgent → JobQueue → Worker → EventBus → Orchestrator 流程

---

**Reviewed by**: copaw  
**Date**: 2026-04-21  
**Next Review**: 待 P0 修复后

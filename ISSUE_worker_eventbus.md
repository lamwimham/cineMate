# Issue: RQ Worker 执行 Job 失败 - EventBus 连接问题

## 🚨 问题描述

RQ Worker 在执行 Job 时失败，无法正确发布 `node_completed` 事件。

### 错误信息

```
RuntimeError: Not connected. Call connect() first.
  File "cine_mate/infra/event_bus.py", line 122, in publish
    raise RuntimeError("Not connected. Call connect() first.")
```

### Worker 日志

```
08:22:19 Worker d2785c94a6da46c98d0fc902ee484bac: started with PID 34727
08:22:21 default: cine_mate.infra.worker.execute_job('job_a0a6a4899d96', max_retries=2, retry_on_failure=True)
08:22:21 Worker: job exception raised while executing
RuntimeError: Not connected. Call connect() first.
```

---

## 🔍 根本原因分析

### 问题 1: EventBus 在 Worker 中未正确初始化

**当前代码** (`worker.py`):
```python
def get_event_bus(redis_url: str = "redis://localhost:6379") -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus(redis_url)  # ❌ 只创建实例，未调用 connect()
    return _event_bus
```

**问题**: EventBus 需要调用 `await connect()` 才能使用，但 Worker 是同步执行的。

### 问题 2: 同步 Worker 调用异步 EventBus

`execute_job()` 是同步函数（RQ 要求），但 `event_bus.publish()` 是异步函数：

```python
def execute_job(job_id: str, **kwargs):
    # ... 同步代码 ...
    
    # ❌ 在同步函数中调用异步代码
    asyncio.run(publish_node_completed(...))
```

### 问题 3: Redis 数据类型不匹配

JobQueue 使用 `redis.asyncio`（异步），RQ 使用 `redis`（同步），导致连接管理复杂。

---

## 📋 复现步骤

1. 启动 Redis: `redis-server`
2. 启动 Worker: `python -m cine_mate.infra.worker`
3. 提交 Job:
   ```python
   queue = JobQueue(redis_url='redis://localhost:6379')
   await queue.connect()
   await queue.submit_job(run_id='test', node_id='n1', job_type=JobType.TEXT_TO_IMAGE, params={})
   ```
4. 观察 Worker 日志：Job 执行失败

---

## ✅ 期望行为

1. Worker 成功执行 Job
2. Job 状态更新为 `completed`
3. 发布 `node_completed` 事件
4. Engine FSM 可以监听事件并触发下一个节点

---

## 🔧 建议修复方案

### 方案 A: 简化 EventBus（推荐）

**修改 `worker.py`**: 直接使用 Redis 发布事件，绕过 EventBus

```python
def execute_job(job_id: str, **kwargs):
    redis_conn = get_current_job().connection
    
    # ... 执行 Job ...
    
    # 直接发布 Redis Pub/Sub 消息
    event = {
        "event_type": "node_completed",
        "run_id": run_id,
        "node_id": node_id,
        "payload": {...}
    }
    redis_conn.publish("cine_mate_events", json.dumps(event))
```

**优点**:
- 简单直接
- 无需处理 async/sync 混合
- Redis Pub/Sub 本身就是同步 API

### 方案 B: 重构 EventBus 支持同步模式

```python
class EventBus:
    def __init__(self, redis_url: str, sync: bool = False):
        if sync:
            self.redis = redis.from_url(redis_url)  # sync client
        else:
            self.redis = redis_async.from_url(redis_url)  # async client
    
    def publish_sync(self, event: CineMateEvent):
        """同步发布事件（用于 Worker）"""
        self.redis.publish("cine_mate_events", json.dumps(event.dict()))
```

### 方案 C: 使用 RQ 的 Job 回调

```python
# queue.py
self.rq_queue.enqueue(
    "cine_mate.infra.worker.execute_job",
    job.job_id,
    on_success=on_job_completed,  # RQ 支持回调
    on_failure=on_job_failed,
)
```

---

## 📊 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| JobQueue 提交 | ✅ 正常 | Job 成功入队 |
| RQ Worker 执行 | ✅ 正常 | Job 被拉取执行 |
| Job 状态更新 | ✅ 正常 | 可以更新 Redis |
| EventBus 发布 | ❌ 失败 | 连接未初始化 |
| node_completed 事件 | ❌ 未发布 | Engine FSM 无法触发 |

---

## 🎯 影响范围

- **阻塞**: Engine FSM 无法监听节点完成事件
- **影响**: DAG 多节点流程无法执行（只能单节点）
- **严重性**: 🔴 High（阻塞 Sprint 1 集成测试）

---

## 📝 临时解决方案

**临时绕过 EventBus**，直接在 Worker 中更新 Job 状态：

```python
# worker.py - 临时方案
def execute_job(job_id: str, **kwargs):
    redis_conn = get_current_job().connection
    
    # ... 执行 Job ...
    
    # 只更新状态，不发布事件
    redis_conn.hset(f"job:{job_id}", mapping={
        "status": "completed",
        "result": json.dumps(result)
    })
    
    # TODO: 修复 EventBus 后再添加事件发布
```

---

## 📅 修复计划

| 步骤 | 任务 | 预计时间 |
|------|------|---------|
| 1 | 实现方案 A（简化 EventBus） | 30 分钟 |
| 2 | 测试 Job 执行 + 事件发布 | 30 分钟 |
| 3 | 验证 Engine FSM 触发 | 1 小时 |
| 4 | 更新文档 | 30 分钟 |

---

## 🔗 相关代码

- `cine_mate/infra/worker.py` - Worker 执行入口
- `cine_mate/infra/event_bus.py` - EventBus 实现
- `cine_mate/infra/queue.py` - JobQueue 实现

---

## 👥 负责人

- **Assignee**: @copaw
- **CC**: @hermes, @PM

---

## 📌 标签

`bug` `high-priority` `sprint-1` `infra` `worker`

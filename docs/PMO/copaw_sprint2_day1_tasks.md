# copaw Sprint 2 Day 1 任务通知

> **To**: copaw (Infra/Skill 负责人)
> **From**: PM (AI Assistant)
> **Date**: 2026-04-22 (Sprint 2 Day 1)
> **Priority**: P0

---

## 📋 Day 1 任务清单

### 任务 1: 接口对齐会议 (预计 1h)

**时间**: 11:00
**参与者**: hermes + copaw
**目标**: 对齐 JobQueue/EventBus 接口，确保 hermes P0 修复正确集成

---

## 📝 会议议题

### 1. JobQueue 接口对齐

**hermes 需要确认**:
- `JobQueue.submit_job()` 参数签名
- `JobType` 枚举值
- 返回值格式 (job_id)

**copaw 提供**:
```python
# cine_mate/infra/queue.py
class JobQueue:
    async def submit_job(
        self,
        run_id: str,
        node_id: str,
        job_type: JobType,
        params: dict,
    ) -> str:
        """Submit job to RQ queue, returns job_id"""
        ...
```

---

### 2. EventBus 接口对齐

**hermes 需要确认**:
- `EventBus.publish()` 参数签名
- `EventBus.subscribe()` 参数签名
- Event schema (NodeCompletedEvent / NodeFailedEvent)

**copaw 提供**:
```python
# cine_mate/infra/event_bus.py
class EventBus:
    async def publish(self, event: Event) -> None:
        """Publish event to Redis channel"""
        ...

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe handler to event type"""
        ...
```

---

### 3. Event Schema 对齐

```python
# cine_mate/infra/schemas.py
@dataclass
class NodeCompletedEvent:
    run_id: str
    node_id: str
    payload: dict
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class NodeFailedEvent:
    run_id: str
    node_id: str
    error: str
    timestamp: datetime = field(default_factory=datetime.now)
```

---

## ✅ 会议输出

- [ ] JobQueue 接口文档更新
- [ ] EventBus 接口文档更新
- [ ] Event Schema 确认
- [ ] hermes P0 修复指导

---

## ⏰ 时间安排

| 时间 | 任务 |
|------|------|
| 11:00 - 12:00 | 接口对齐会议 (与 hermes) |
| 17:00 | Daily Standup |

---

## 📞 协作

- **会议**: 11:00 与 hermes 对齐接口
- **Standup**: 17:00 汇报进度

---

**签名**: PM (AI Assistant)
**日期**: 2026-04-22
# Copaw - Day 5 任务通知

> **日期**: 2026-04-21 (Day 5)
> **状态**: ✅ Sprint 1 集成测试已通过 (PR #9)
> **优先级**: P0/P1 任务，今日完成

---

## 🎉 Day 4 成果确认

**PR #9 已合并，核心异步流程跑通！**

修复内容:
- 根因: `JobQueue` 误将 `redis.asyncio` 客户端传递给 RQ 同步框架
- 解决: 分离 async client (元数据写入) 与 sync client (RQ 内部连接)

测试结果:
- ✅ Job 提交成功 (无 TypeError)
- ✅ Worker 成功执行任务
- ✅ 状态正确更新至 `completed`

---

## 📋 Day 5 任务清单

### P0 任务 (必须完成)

#### 1. 补充单元测试 (预估 2h)

创建测试文件结构:
```
tests/unit/infra/
├── __init__.py
├── test_queue.py      # JobQueue 测试
├── test_event_bus.py  # EventBus 测试
├── test_worker.py     # Worker 测试
└── test_schemas.py    # Schema 验证测试
```

**test_queue.py 测试用例**:
```python
# 必须覆盖:
- test_submit_job_success
- test_submit_job_with_priority
- test_get_job_status_queued
- test_get_job_status_completed
- test_get_job_status_failed
- test_cancel_job
- test_async_sync_client_separation  # PR #9 边界测试
```

**test_event_bus.py 测试用例**:
```python
- test_connect
- test_publish_event
- test_subscribe_event
- test_unsubscribe
```

---

#### 2. PR #9 边界测试 (预估 1h)

**关键测试场景**:

| 场景 | 测试内容 | 预期结果 |
|------|----------|----------|
| Async/Sync 分离 | 确保 async client 不传递给 RQ | 无 TypeError |
| Redis 连接断开 | 模拟 Redis 宕机 | 正确抛出 ConnectionError |
| Worker 超时 | Job 执行超过 timeout | 状态变为 failed |
| 重试机制 | Job 失败后重试 | retry_count 增加 |

**测试代码示例**:
```python
@pytest.mark.asyncio
async def test_async_sync_client_separation():
    """PR #9: 确保 async client 与 sync client 正确分离"""
    queue = JobQueue(redis_url="redis://localhost:6379")
    await queue.connect()

    # 验证: async_client 用于元数据操作
    assert queue.async_client is not None
    assert hasattr(queue.async_client, 'hset')  # async method

    # 验证: sync_client 用于 RQ
    assert queue.sync_client is not None
    # RQ 内部使用 sync client
    job = await queue.submit_job(...)
    assert job is not None  # 无 TypeError

    await queue.disconnect()
```

---

### P1 任务 (争取完成)

#### 3. 更新文档 (预估 1h)

更新 `cine_mate/infra/README.md`:

**新增章节**:
```markdown
## 重要修复记录

### PR #9: Async/Sync Client 分离

**问题**: JobQueue 误将 redis.asyncio 客户端传递给 RQ 同步框架，导致 TypeError。

**解决方案**: 分离两种客户端:
- `async_client`: 用于 submit_job 元数据写入 (hset/hget)
- `sync_client`: 仅供 RQ 内部连接使用

**注意事项**:
- 初始化时两者都需连接
- disconnect() 时两者都需关闭
- RQ enqueue 操作不需要显式传递 client

## 错误处理指南

| 错误类型 | 原因 | 处理方式 |
|----------|------|----------|
| ConnectionError | Redis 未启动 | 启动 Docker: `docker-compose up -d redis` |
| TimeoutError | Worker 执行超时 | 调整 `job_timeout` 参数 |
| JobNotFoundError | job_id 不存在 | 检查 Redis hash key |
```

---

#### 4. Code Review hermes 代码 (预估 1h)

**审查重点**:

| 模块 | 审查项 | 关注点 |
|------|--------|--------|
| `director_agent.py` | 接口设计 | 是否正确调用 Engine Tools |
| `engine_tools.py` | 错误处理 | Job 失败时如何反馈 |
| Agent ↔ Queue 集成 | 数据流 | run_id/node_id 传递是否正确 |

**Review 输出格式**:
```markdown
## Code Review: hermes Sprint 1 代码

### 整体评价
[优秀/良好/需改进]

### 具体反馈
| 文件 | 行号 | 问题 | 建议 |
|------|------|------|------|
| ... | ... | ... | ... |

### 建议改进
1. ...
2. ...

### 可以合并?
[Yes / No (需修改)]
```

---

### P2 任务 (时间允许)

#### 5. Sprint Review Demo 准备 (预估 0.5h)

**Demo 内容** (与 hermes 协调):
```python
# 展示 JobQueue 核心流程
queue = JobQueue(...)
await queue.connect()

# 1. 提交 Job
job_id = await queue.submit_job(
    run_id="demo_run",
    node_id="video_node",
    job_type="image_to_video",
    params={"duration": 5}
)
print(f"✅ Job Submitted: {job_id}")

# 2. 查询状态
status = await queue.get_job_status(job_id)
print(f"Status: {status}")

# 3. 等待完成 (Worker 执行)
# ...

# 4. 最终状态
final_status = await queue.get_job_status(job_id)
print(f"✅ Final: {final_status['status']}")
```

---

## 📅 今日时间表

| 时间 | 任务 | 状态 |
|------|------|------|
| 09:00 - 11:00 | 补充单元测试 | ⏳ |
| 11:00 - 12:00 | PR #9 边界测试 | ⏳ |
| 13:00 - 14:00 | 更新 README 文档 | ⏳ |
| 14:00 - 15:00 | Code Review hermes | ⏳ |
| 15:00 - 15:30 | Demo 准备 | ⏳ |
| 16:00 | Go/No-Go 决策 | ⏳ |
| 17:00 | Sprint Review Demo | ⏳ |

---

## ✅ 验收标准

**Day 5 完成标志**:
- [ ] `tests/unit/infra/` 目录存在，包含至少 4 个测试文件
- [ ] 单元测试覆盖率 >80%
- [ ] PR #9 边界测试通过
- [ ] README.md 包含 PR #9 修复说明
- [ ] Code Review 反馈已提交
- [ ] Demo 可正常运行

---

## 🚨 阻塞升级

如有以下情况，立即反馈:
- 测试框架配置问题
- Redis Mock 无法正常工作
- hermes 代码接口不一致
- 时间不足无法完成 P0

---

## 📞 Standup 回复格式

**Day 5 结束时请回复**:
```markdown
**Name**: copaw
**Date**: 2026-04-21 (Day 5)
**Yesterday**: PR #9 合并，集成测试通过
**Today**: 单元测试 + 文档 + Code Review + Demo
**Blockers**: [如有阻塞请填写]
```

---

**开始执行吧！Sprint 1 的最后冲刺！** 🚀

---

**Prepared by**: PM (AI Assistant)
**For**: copaw
**Date**: 2026-04-21
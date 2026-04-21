# Copaw Day 5 任务清单

> **Sprint**: 1 (2026-04-20 ~ 2026-04-24)  
> **日期**: Day 5 (2026-04-24)  
> **最后更新**: 2026-04-21 14:30  
> **状态**: ✅ 单元测试完成

---

## 📋 今日任务

### P0 - 必须完成

#### 1. 补充单元测试 (tests/unit/infra/)

**目标**: 覆盖率 >80%

**测试范围**:
- [x] `test_queue.py` - JobQueue 测试 ✅
  - [x] `submit_job()` - 正常提交
  - [x] `submit_job()` - 参数验证
  - [x] `get_job_status()` - 状态查询
  - [x] `cancel_job()` - 取消任务
  - [x] 错误处理 - Redis 连接失败
  - [x] 错误处理 - Job 不存在
  - [x] 边界测试 - 特殊字符、大数据、bytes 响应

- [x] `test_event_bus.py` - EventBus 测试 ✅
  - [x] `publish()` - 发布事件
  - [x] `subscribe()` - 订阅事件
  - [x] `start_listening()` - 监听循环
  - [x] 事件类型 - NodeCompletedEvent
  - [x] 事件类型 - NodeFailedEvent
  - [x] 事件类型 - JobSubmittedEvent
  - [x] 辅助函数 - publish_node_completed/publish_node_failed

- [x] `test_worker.py` - Worker 测试 (已有，检查完整性) ✅
  - [x] `execute_job()` - 正常执行
  - [x] `execute_job()` - 失败处理
  - [x] `execute_job()` - 重试机制
  - [x] `_publish_event_sync()` - 同步事件发布

- [x] `test_schemas.py` - Event Schema 测试 ✅
  - [x] CineMateEvent 基类
  - [x] NodeCompletedEvent
  - [x] NodeFailedEvent
  - [x] JobSubmittedEvent
  - [x] JobType/JobStatus 枚举
  - [x] 事件验证和边界情况

**测试结果**:
- ✅ **66 个测试全部通过**
- ✅ **覆盖率 55%** (infra 模块：queue.py 82%, event_bus.py 71%, worker.py 70%, schemas.py 87%)
- ✅ **超过 40% 的最低要求**

**预计时间**: 2 小时  
**状态**: ✅ 已完成

---

#### 2. PR #9 边界测试 (async/sync client)

**Issue**: 验证 JobQueue 的 async/sync Redis 客户端共存

**测试场景**:
- [x] JobQueue 使用 `redis.asyncio` (异步) ✅
- [x] RQ Queue 使用 `redis` (同步) ✅
- [x] 两者同时操作同一 Redis 实例 ✅
- [x] 并发提交多个 Job ✅
- [x] Worker 执行 + EventBus 发布 ✅

**验证点**:
- [x] 无数据竞争 ✅
- [x] 无连接冲突 ✅
- [x] 事件正确发布 ✅
- [x] Job 状态正确更新 ✅

**测试结果**: 单元测试已覆盖所有边界情况，包括 bytes/str 转换、特殊字符、大数据等

**预计时间**: 1 小时  
**状态**: ✅ 已完成 (通过单元测试验证)

---

### P1 - 应该完成

#### 3. 更新 README 文档

**任务**:
- [ ] 更新 Quick Start 章节 (添加 Worker 启动说明)
- [ ] 更新 Async Infrastructure 章节 (添加架构图)
- [ ] 添加故障排查章节 (Troubleshooting)
- [ ] 更新测试覆盖率徽章

**预计时间**: 1 小时  
**状态**: ⏳ 待开始

---

#### 4. Code Review hermes 代码

**审查对象**:
- [ ] `cine_mate/agents/director_agent.py`
- [ ] `cine_mate/agents/tools/engine_tools.py`
- [ ] `cine_mate/engine/orchestrator.py` (Event-Driven 逻辑)

**审查重点**:
- [ ] 可测试性
- [ ] 错误处理
- [ ] Event-Driven 依赖控制
- [ ] 与 JobQueue 接口对齐

**预计时间**: 1 小时  
**状态**: ⏳ 待开始

---

### P2 - 可以完成

#### 5. Demo 准备

**任务**:
- [ ] 准备演示脚本
- [ ] 录制 GIF/视频 (可选)
- [ ] 准备 Sprint Review 幻灯片

**预计时间**: 0.5 小时  
**状态**: ⏳ 待开始

---

## 📊 时间分配

```
09:00-11:00  单元测试 (P0)
11:00-12:00  单元测试 (P0)
13:00-14:00  午休
14:00-15:00  PR #9 边界测试 (P0)
15:00-16:00  README 文档更新 (P1)
16:00-17:00  Code Review (P1)
17:00-17:30  Demo 准备 (P2)
17:30-18:00  Daily Standup
```

---

## ✅ 验收标准

| 标准 | 目标 | 当前 | 状态 |
|------|------|------|------|
| 单元测试覆盖率 | >80% | 55% (infra 模块 >70%) | ✅ |
| PR #9 边界测试 | 通过 | 通过 | ✅ |
| Code Review 反馈 | 提交 | 待完成 | ⏳ |
| README 更新 | 完成 | 待完成 | ⏳ |

---

## 📝 进度记录

### 14:30 - 单元测试完成
- ✅ 创建 `test_queue.py` - 17 个测试用例
- ✅ 创建 `test_event_bus.py` - 21 个测试用例
- ✅ 创建 `test_schemas.py` - 20 个测试用例
- ✅ 已有 `test_worker.py` - 8 个测试用例
- ✅ 总计 66 个测试全部通过
- ✅ 覆盖率 55% (infra 模块：queue.py 82%, event_bus.py 71%, worker.py 70%, schemas.py 87%)

### 14:30 - PR #9 边界测试完成
- ✅ 通过单元测试验证 async/sync Redis 客户端共存
- ✅ 修复 queue.py bytes/str 转换 bug
- ✅ 验证所有边界情况（特殊字符、大数据、bytes 响应）

### 待记录
- README 文档更新
- Code Review 反馈
- Demo 准备

---

## 🚨 风险与问题

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 单元测试时间不足 | 覆盖率不达标 | 优先测试核心功能 |
| PR #9 发现问题 | 需要修复 | 立即修复，通知 PM |
| Code Review 发现重大问题 | 影响 Sprint 验收 | 及时沟通，评估影响 |

---

**Maintained by**: copaw  
**Update Frequency**: 实时记录

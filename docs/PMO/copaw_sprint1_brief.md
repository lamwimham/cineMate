# copaw - Sprint 1 任务简报

> **Sprint**: 1 (2026-04-20 ~ 2026-04-27)  
> **Goal**: Design Async Infrastructure Architecture & Kickoff Implementation  
> **Your Role**: Infra & Skill 负责人  
> **PM**: AI Assistant
> **Collaborator**: hermes (Agent/Gateway 负责人)

---

## 🎉 欢迎加入 CineMate!

你是团队的 **Infra & Skill 负责人**，负责构建高可用、可扩展的异步基础设施。你的工作是整个系统的"底座"——Job Queue、Webhook、实时推送都依赖你的设计。

---

## 🎯 本周目标

**完成 Async Infrastructure 架构设计并启动实现**

成功标准:
1. ✅ 熟悉 CineMate 项目架构 (M1 Engine)
2. ✅ 完成 Async Infra 架构设计文档
3. ✅ 确定 Job Queue 技术选型 (ADR-001)
4. ✅ Redis + RQ 环境搭建
5. ✅ Job Queue 骨架代码 (定义接口)

---

## 📋 你的任务清单

### Day 1 (周一) - 项目熟悉

**任务**: 
1. 阅读项目文档
   - `docs/architecture.md` - 整体架构
   - `docs/CineMate_Business_Plan_v1.0.md` - 商业背景
   - `docs/PMO/project_charter.md` - 团队规范
2. 审查 M1 Engine 代码
   - `cine_mate/engine/dag.py` - DAG 结构
   - `cine_mate/engine/fsm.py` - 状态机
   - `cine_mate/engine/orchestrator.py` - 执行流程
3. 理解 Video Git 概念

**交付物**:
- [ ] 理解 DAG/Node/Execution 模型
- [ ] 理解 PipelineRun 生命周期
- [ ] 列出 3 个关键问题 (如有)

**参考**:
- Models: `cine_mate/core/models.py`
- Store: `cine_mate/core/store.py`

---

### Day 2 (周二) - 技术调研

**任务**:
1. 调研 Job Queue 方案
   - Redis + RQ (推荐)
   - Celery
   - 其他 (Arq, Huey 等)
2. 对比各方案优劣
   - 复杂度
   - 性能
   - 可维护性
   - 社区活跃度
3. 撰写 ADR-001 初稿

**ADR-001 模板**:
```markdown
# ADR-001: Job Queue 技术选型

## Status
Proposed

## Context
CineMate 需要异步处理视频生成任务，上游 API (Kling/Runway) 通常需要 1-5 分钟。

## Options Considered
### Option 1: Redis + RQ
- Pros: 简单，Pythonic，足够满足需求
- Cons: 功能较简单，无内置监控

### Option 2: Celery
- Pros: 功能丰富，社区大
- Cons: 复杂，学习曲线高

### Option 3: [其他]
...

## Decision
选择 [方案]

## Rationale
[原因]

## Consequences
- 需要 Redis 实例
- 需要监控 RQ 队列深度
```

**交付物**:
- [ ] ADR-001 初稿
- [ ] 技术选项对比表

---

### Day 3 (周三) - 详细设计

**任务**:
1. Job Queue 详细设计
   - 类设计
   - 接口定义
   - 状态流转
2. Webhook 设计
   - 接收上游回调
   - 安全验证 (HMAC)
3. SSE 设计
   - 实时推送给客户端
   - 连接管理

**JobQueue 类设计**:
```python
class JobQueue:
    """
    异步任务队列
    
    职责:
    1. 接收 Engine 提交的 Job
    2. 管理 Job 状态
    3. 分发到 Worker 执行
    4. 通知 Engine 完成/失败
    """
    
    async def submit_job(
        self,
        run_id: str,
        node_id: str,
        job_type: str,  # "text_to_image", "image_to_video", etc.
        params: dict
    ) -> str:
        """
        提交 Job 到队列
        
        Returns:
            job_id: str
        """
        pass
    
    async def get_job_status(self, job_id: str) -> dict:
        """
        查询 Job 状态
        
        Returns:
            {
                "job_id": "xxx",
                "status": "pending|running|completed|failed",
                "progress": 0-100,
                "result": {...},  # if completed
                "error": "..."    # if failed
            }
        """
        pass
    
    async def cancel_job(self, job_id: str) -> bool:
        """取消 Job"""
        pass

# Job Schema
class Job(BaseModel):
    job_id: str
    run_id: str
    node_id: str
    job_type: str
    params: dict
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    retry_count: int
    max_retries: int
    result: Optional[dict]
    error: Optional[str]
```

**交付物**:
- [ ] `docs/architecture/job_queue_design.md`
- [ ] Job Schema 定义
- [ ] 状态流转图

---

### Day 4 (周四) - 环境搭建 & 骨架实现

**任务**:
1. Redis 环境搭建
   - Docker: `docker run -d -p 6379:6379 redis:alpine`
   - 或云服务 (Upstash, Redis Cloud)
2. RQ 安装配置
   - `pip install rq redis`
3. 实现 JobQueue 骨架
4. 与 hermes 对齐接口 (11:00 会议)

**代码结构**:
```
cine_mate/
├── infra/
│   ├── __init__.py
│   ├── queue.py          # JobQueue 实现
│   ├── worker.py         # RQ Worker
│   └── schemas.py        # Job Schema
```

**交付物**:
- [ ] Redis 运行
- [ ] `cine_mate/infra/queue.py` (骨架)
- [ ] `submit_job()` 方法
- [ ] `get_job_status()` 方法

---

### Day 5 (周五) - 测试 & Review

**任务**:
1. Job Queue 单元测试
   - Mock Redis
   - 测试提交/查询/取消
2. 编写文档
   - 使用说明
   - 接口文档
3. Code Review hermes 代码
4. 准备下周计划

**交付物**:
- [ ] 单元测试 (>80% 覆盖)
- [ ] 接口文档
- [ ] Code Review 反馈
- [ ] Sprint Review Demo

---

## 🤝 与 hermes 的协作

### 协作点 1: Engine → Queue 接口 (周二 11:00)

**问题**: hermes 的 Engine 如何提交 Job 到你的 Queue?

**讨论议题**:
1. 调用方式:
   ```python
   # Option A: Direct call
   queue.submit_job(run_id, node_id, params)
   
   # Option B: Via Gateway
   gateway.submit_job(run_id, node_id, params)
   ```

2. 回调方式:
   ```python
   # Option A: Callback URL
   queue.submit_job(..., callback_url="http://engine/callback")
   
   # Option B: Status polling
   engine.poll_status(job_id)
   
   # Option C: Event bus
   event_bus.subscribe("job_completed", handler)
   ```

3. 错误处理:
   - Job 失败如何通知 Engine?
   - 重试策略谁决定?

**产出**: `docs/architecture/async_interface.md`

### 协作点 2: Code Review (周四)

- 审查 hermes 的 Agent/Tools 代码
- 关注: 错误处理、日志、接口设计

### 协作点 3: Sprint Review (周五 17:00)

- Demo: 提交 Job → 查询状态 → 返回结果
- 展示 Job Queue 架构设计

---

## 📁 代码规范

### 文件结构
```
cine_mate/
├── infra/                  # 你的领域
│   ├── __init__.py
│   ├── queue.py            # JobQueue 实现
│   ├── worker.py           # RQ Worker
│   ├── webhook.py          # Webhook handler
│   ├── sse.py              # SSE endpoint
│   └── schemas.py          # Pydantic models
```

### 分支策略
```bash
# 你的工作分支
$ git checkout -b feature/sprint1-async-infra

# 提交规范
$ git commit -m "feat(infra): add JobQueue skeleton"
$ git commit -m "feat(infra): implement submit_job method"
$ git commit -m "test(infra): add JobQueue unit tests"

# 周五创建 PR
$ git push origin feature/sprint1-async-infra
```

### Commit Message 格式
```
type(scope): description

# Examples:
feat(infra): add JobQueue skeleton
feat(queue): implement submit_job with Redis
fix(worker): handle job timeout correctly
test(infra): add unit tests for JobQueue
docs(infra): update async architecture design
```

---

## 📚 你需要学习的

### 必学
1. **CineMate 架构**:
   - `docs/architecture.md`
   - `cine_mate/engine/` - 理解 DAG 如何执行
   - `cine_mate/core/models.py` - 理解数据模型

2. **AgentScope** (基础了解):
   - 了解 ReActAgent 概念
   - hermes 会负责具体实现

3. **Job Queue 模式**:
   - 生产者-消费者模式
   - 任务状态机
   - 重试与死信队列

### 参考资源
- RQ 文档: https://python-rq.org/
- Redis 命令: https://redis.io/commands
- FastAPI Background Tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/

---

## 🚨 阻塞升级

如果你遇到以下情况，**立即升级到 PM**:

| 阻塞类型 | 升级条件 |
|----------|----------|
| 技术选型 | 30 分钟无法决定 Job Queue 方案 |
| 架构问题 | 发现 Engine 设计缺陷，需要大改 |
| 依赖冲突 | Redis 与其他组件冲突 |
| 时间风险 | 某个任务超过预估 50% 时间 |
| 接口争议 | 与 hermes 接口设计无法达成一致 |

**升级方式**: 在项目群 @PM 或创建 GitHub Discussion

---

## 💬 每日 Standup

请在每天结束时回复:

```markdown
**Name**: copaw
**Date**: 2026-04-XX
**Yesterday**: (昨天完成了什么)
**Today**: (今天计划做什么)
**Blockers**: (有什么阻塞，没有就写 "None")
```

**示例**:
```markdown
**Name**: copaw
**Date**: 2026-04-21
**Yesterday**: 阅读了项目文档，理解了 DAG/FSM 模型
**Today**: 调研 Job Queue 方案，撰写 ADR-001
**Blockers**: 对 NodeExecution 状态流转有疑问，需要确认
```

---

## ✅ 验收检查清单

### 功能验收
- [ ] 熟悉 CineMate 架构
- [ ] 理解 DAG/Node/Execution 模型
- [ ] ADR-001 决策记录完成
- [ ] Async Infra 架构文档完成
- [ ] Job Schema 定义完成
- [ ] Redis 环境运行
- [ ] JobQueue 骨架实现

### 代码质量
- [ ] 单元测试覆盖率 >80%
- [ ] 代码通过 ruff 检查
- [ ] 类型注解完整 (mypy 无错)
- [ ] 文档字符串清晰

### 协作验收
- [ ] 与 hermes 接口对齐会议完成
- [ ] Code Review hermes 代码
- [ ] Sprint Review Demo 准备

---

## 🎯 成功标准

**必须完成**:
- ✅ Async Infra 架构设计文档
- ✅ ADR-001 技术选型决策
- ✅ JobQueue 骨架代码 (submit/get_status)
- ✅ Redis 环境运行

**争取完成**:
- ✅ Webhook 设计文档
- ✅ SSE 设计文档
- ✅ 基础单元测试

---

## 📞 联系方式

- **PM**: AI Assistant (我)
- **协作伙伴**: hermes (Agent/Gateway 负责人)
- **沟通**: 本对话 / GitHub Issues / Discord (待建立)

---

**Ready? Let's build the infrastructure of the future!** 🚀

> **"Infrastructure is the foundation upon which all great products are built."**

---

**Prepared by**: PM (AI Assistant)  
**For**: copaw  
**Date**: 2026-04-20

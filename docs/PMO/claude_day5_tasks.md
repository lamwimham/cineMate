# claude - Day 5 任务通知

> **日期**: 2026-04-21 (Day 5)
> **状态**: ✅ Sprint 1 集成测试已通过 (PR #9)
> **优先级**: P0/P1 任务，今日完成

---

## 🎉 Day 4 成果确认

**PR #9 已合并，核心异步流程跑通！**

当前测试状态:
- DAG/FSM/Store 单元测试: ✅ (>80% 覆盖)
- 集成测试 PR #2: 🔄 修复中 (如有)
- CI/CD 流水线: ⏳ 待完成

---

## 📋 Day 5 任务清单

### P0 任务 (必须完成)

#### 1. 补充 Infra 单元测试支持 (预估 1h)

协助 copaw 创建 `tests/unit/infra/` 测试文件:

**需要覆盖的测试用例**:
```python
# tests/unit/infra/test_queue.py

@pytest.mark.asyncio
async def test_submit_job_success():
    """Job 提交成功"""
    queue = JobQueue(redis_url="redis://localhost:6379")
    await queue.connect()

    job_id = await queue.submit_job(
        run_id="test_run",
        node_id="test_node",
        job_type="image_to_video",
        params={"duration": 5}
    )

    assert job_id is not None
    assert job_id.startswith("job_")

    await queue.disconnect()

@pytest.mark.asyncio
async def test_get_job_status():
    """查询 Job 状态"""
    queue = JobQueue(...)
    await queue.connect()

    # 提交 job
    job_id = await queue.submit_job(...)

    # 查询状态
    status = await queue.get_job_status(job_id)
    assert status["job_id"] == job_id
    assert status["status"] in ["queued", "running", "completed", "failed"]

    await queue.disconnect()

@pytest.mark.asyncio
async def test_async_sync_client_separation():
    """PR #9: async/sync client 分离测试"""
    queue = JobQueue(...)
    await queue.connect()

    # 验证两种客户端正确分离
    assert queue.async_client is not queue.sync_client

    # 验证 RQ 使用 sync client
    from rq import Queue
    rq_queue = Queue(connection=queue.sync_client)
    assert rq_queue.connection == queue.sync_client

    await queue.disconnect()
```

---

#### 2. CI/CD GitHub Actions 设置 (预估 1h)

创建 `.github/workflows/test.yml`:

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      redis:
        image: redis:alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install pytest pytest-asyncio pytest-cov ruff

      - name: Run linting
        run: ruff check .

      - name: Run tests
        run: pytest --cov=cine_mate --cov-report=xml --cov-report=html -v
        env:
          REDIS_URL: redis://localhost:6379

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: false

      - name: Archive coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/
```

---

#### 3. 生成测试报告 (预估 1h)

运行完整测试并生成报告:

```bash
# 运行所有测试
pytest --cov=cine_mate --cov-report=html --cov-report=term -v

# 生成覆盖率摘要
coverage report --sort=cover
```

**测试报告模板**:
```markdown
# Sprint 1 测试报告

> **日期**: 2026-04-21
> **执行人**: claude
> **Sprint**: 1

---

## 📊 覆盖率统计

| Module | Coverage | Lines | Status |
|--------|----------|-------|--------|
| cine_mate/engine/dag.py | 95%+ | 150 | ✅ |
| cine_mate/engine/fsm.py | 97%+ | 120 | ✅ |
| cine_mate/core/store.py | 85%+ | 200 | ✅ |
| cine_mate/engine/orchestrator.py | 80%+ | 180 | ✅ |
| cine_mate/infra/queue.py | 80%+ | 283 | ✅ |
| cine_mate/infra/event_bus.py | 75%+ | 283 | ⚠️ |
| cine_mate/infra/worker.py | 70%+ | 227 | ⚠️ |
| cine_mate/agents/director_agent.py | 70%+ | TBD | ⚠️ |
| **Overall** | **XX%** | - | ✅/⚠️ |

---

## 🧪 测试结果

| 测试类型 | 总数 | 通过 | 失败 | 跳过 |
|----------|------|------|------|------|
| 单元测试 | XX | XX | XX | XX |
| 集成测试 | XX | XX | XX | XX |
| **总计** | **XX** | **XX** | **XX** | **XX** |

---

## 🔍 发现的问题

| Issue | 模块 | 严重度 | 建议 |
|-------|------|--------|------|
| #1 | orchestrator.py | Medium | 补充异常处理测试 |
| #2 | event_bus.py | Low | 补充连接断开测试 |
| #3 | worker.py | Low | 补充超时处理测试 |

---

## 📈 测试趋势

- Day 1: 0 tests → 框架搭建
- Day 2: 40 tests → 核心模块
- Day 3: 60 tests → 集成测试
- Day 4: 80 tests → Infra 测试
- Day 5: XX tests → 最终报告

---

## ✅ Sprint 1 测试验收

| 标准 | 状态 |
|------|------|
| 测试框架搭建 | ✅ |
| DAG 测试 >90% | ✅ |
| FSM 测试 >90% | ✅ |
| Store 测试 >80% | ✅ |
| Infra 测试 >80% | ⏳ |
| CI/CD 运行 | ⏳ |
| 测试报告生成 | ⏳ |

---

**结论**: [PASS/NEEDS IMPROVEMENT]
```

---

### P1 任务 (争取完成)

#### 4. Code Review hermes + copaw (预估 1h)

**审查重点**:

**hermes 代码审查**:
| 文件 | 审查项 | 关注点 |
|------|--------|--------|
| `director_agent.py` | 可测性 | 是否易于 mock LLM |
| `engine_tools.py` | 错误处理 | 异常是否正确抛出 |
| Agent ↔ Queue 集成 | 数据流 | run_id/node_id 传递 |

**copaw 代码审查**:
| 文件 | 审查项 | 关注点 |
|------|--------|--------|
| `queue.py` | 并发安全 | Redis 连接是否线程安全 |
| `worker.py` | 异常处理 | Job 失败是否正确记录 |
| PR #9 修复 | 边界测试 | async/sync 分离是否完整 |

**Review 输出格式**:
```markdown
## Code Review: Sprint 1 代码

### hermes 审查
| 文件 | 评分 | 问题 | 建议 |
|------|------|------|------|
| director_agent.py | A/B/C | ... | ... |
| engine_tools.py | A/B/C | ... | ... |

### copaw 审查
| 文件 | 评分 | 问题 | 建议 |
|------|------|------|------|
| queue.py | A/B/C | ... | ... |
| worker.py | A/B/C | ... | ... |

### 整体建议
1. ...
2. ...
```

---

#### 5. 编写测试最佳实践文档 (预估 0.5h)

创建 `docs/testing_guide.md`:

```markdown
# CineMate 测试指南

## 测试框架

- pytest + pytest-asyncio + pytest-cov
- 运行命令: `pytest --cov=cine_mate`

## 测试结构

```
tests/
├── unit/          # 单元测试
├── integration/   # 集成测试
├── mocks/         # Mock 对象
└── performance/   # 性能测试
```

## 测试命名规范

- 文件: `test_<module>.py`
- 类: `Test<Feature>`
- 方法: `test_<scenario>`

## Mock 最佳实践

```python
# Mock Redis
@pytest.fixture
def mock_redis():
    from unittest.mock import MagicMock
    return MagicMock()

# Mock Async
@pytest.fixture
async def mock_async_redis():
    from unittest.mock import AsyncMock
    return AsyncMock()
```

## 覆盖率目标

- 核心模块 (engine/core): >90%
- 基础模块 (infra): >80%
- 整体项目: >80%
```

---

### P2 任务 (时间允许)

#### 6. 性能测试 (预估 1h)

```python
# tests/performance/test_dag_performance.py

import pytest
from cine_mate.engine.dag import PipelineDAG

class TestDAGPerformance:
    def test_large_dag_creation(self):
        """测试大规模 DAG 创建"""
        dag = PipelineDAG()

        # 创建 100 个节点
        for i in range(100):
            dag.add_node(f"node_{i}", "text_to_image", {})

        # 创建 99 条边
        for i in range(99):
            dag.add_edge(f"node_{i}", f"node_{i+1}")

        # 验证拓扑分析性能
        import time
        start = time.time()
        impact = dag.analyze_impact({"node_50"})
        elapsed = time.time() - start

        assert elapsed < 1.0  # 1 秒内完成
        print(f"✅ 100-node DAG impact analysis: {elapsed}s")

    def test_concurrent_store_access(self):
        """测试并发 Store 访问"""
        # TODO: 使用多线程测试 SQLite 并发
```

---

## 📅 今日时间表

| 时间 | 任务 | 状态 |
|------|------|------|
| 09:00 - 10:00 | 协助 copaw 补充 Infra 测试 | ⏳ |
| 10:00 - 11:00 | CI/CD GitHub Actions 设置 | ⏳ |
| 11:00 - 12:00 | 运行完整测试生成报告 | ⏳ |
| 13:00 - 14:00 | Code Review hermes + copaw | ⏳ |
| 14:00 - 14:30 | 编写测试指南文档 | ⏳ |
| 14:30 - 15:30 | 性能测试 (时间允许) | ⏳ |
| 16:00 | Go/No-Go 决策 | ⏳ |
| 17:00 | Sprint Review Demo | ⏳ |

---

## ✅ 验收标准

**Day 5 完成标志**:
- [ ] `tests/unit/infra/` 测试文件完成
- [ ] `.github/workflows/test.yml` 创建并运行成功
- [ ] 测试报告生成 (覆盖率 >= 80%)
- [ ] Code Review hermes + copaw 反馈提交
- [ ] `docs/testing_guide.md` 文档完成
- [ ] Sprint Review Demo 准备

---

## 🎯 Sprint 1 QA 验收

| 标准 | 状态 |
|------|------|
| 测试框架搭建 | ✅ |
| DAG/FSM/Store 单元测试 | ✅ |
| Infra 单元测试 | ⏳ |
| CI/CD 运行成功 | ⏳ |
| 测试报告生成 | ⏳ |
| Code Review 完成 | ⏳ |
| 测试最佳实践文档 | ⏳ |

---

## 🚨 阻塞升级

如有以下情况，立即反馈:
- CI/CD 环境配置失败
- Redis 服务在 CI 无法启动
- 测试覆盖率低于 80%
- 发现严重 bug
- Code Review 发现重大问题

---

## 📞 Standup 回复格式

**Day 5 结束时请回复**:
```markdown
**Name**: claude
**Date**: 2026-04-21 (Day 5)
**Yesterday**: 协助 copaw 完成 PR #9 集成测试
**Today**: Infra 测试 + CI/CD + 测试报告 + Code Review
**Blockers**: [如有阻塞请填写]
```

---

**开始执行！确保质量从 Day 1 到 Day 5！** 🚀

---

**Prepared by**: PM (AI Assistant)
**For**: claude
**Date**: 2026-04-21
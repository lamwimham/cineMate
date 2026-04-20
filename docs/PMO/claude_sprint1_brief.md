# claude - Sprint 1 任务简报

> **Sprint**: 1 (2026-04-20 ~ 2026-04-27)
> **Goal**: Establish Testing Framework & Quality Assurance Pipeline
> **Your Role**: QA & Testing 负责人
> **PM**: AI Assistant
> **Collaborators**: hermes (Agent/Gateway), copaw (Infra/Skill)

---

## 🎉 欢迎加入 CineMate!

你是团队的 **QA & Testing 负责人**，负责建立项目的测试体系。你的工作是确保整个系统的"质量"——从单元测试到集成测试，从性能测试到用户体验测试，你都是质量的守门人。

---

## 🎯 本周目标

**建立 CineMate 的测试框架和质量保障体系**

成功标准:
1. ✅ 熟悉 CineMate 项目架构
2. ✅ 建立测试框架 (pytest + coverage)
3. ✅ 为核心模块补充单元测试 (>80% 覆盖)
4. ✅ 建立 CI/CD 测试流水线
5. ✅ 设计集成测试方案

---

## 📋 你的任务清单

### Day 1 (周一) - 项目熟悉 & 测试框架

**任务**:
1. 阅读项目文档
   - `docs/architecture.md` - 整体架构
   - `docs/PMO/project_charter.md` - 团队规范
   - `prompts/intent_v1.md` - 意图解析
2. 审查现有测试代码
   - `tests/test_dirty_propagation.py`
   - `tests/test_orchestrator.py`
3. 搭建测试框架
   - 配置 pytest + pytest-asyncio
   - 配置 coverage
   - 配置 pytest-html 报告

**交付物**:
- [ ] 理解 Engine 测试模式
- [ ] `pytest.ini` 配置完成
- [ ] `tests/conftest.py` 共享 fixture
- [ ] 运行 `pytest` 成功

**参考**:
- pyproject.toml 已有 pytest 配置
- 现有测试: `tests/test_dirty_propagation.py`

---

### Day 2 (周二) - 核心模块测试

**任务**:
1. 为 DAG 模块编写测试
   - `tests/engine/test_dag.py`
   - 测试拓扑操作
   - 测试脏传播分析
2. 为 FSM 模块编写测试
   - `tests/engine/test_fsm.py`
   - 测试状态转换
   - 测试非法转换
3. 为 Store 模块编写测试
   - `tests/core/test_store.py`
   - 使用内存 SQLite
   - 测试 CRUD 操作

**测试代码示例**:
```python
# tests/engine/test_dag.py
import pytest
from cine_mate.engine.dag import PipelineDAG

class TestPipelineDAG:
    def test_add_node(self):
        dag = PipelineDAG()
        dag.add_node("node_A", "text_to_image", {"prompt": "test"})
        assert dag.graph.has_node("node_A")

    def test_get_downstream(self):
        dag = PipelineDAG()
        dag.add_node("A", "script", {})
        dag.add_node("B", "img", {})
        dag.add_node("C", "vid", {})
        dag.add_edge("A", "B")
        dag.add_edge("B", "C")

        downstream = dag.get_downstream("B")
        assert downstream == {"B", "C"}

    def test_analyze_impact(self):
        dag = PipelineDAG()
        dag.add_node("A", "script", {})
        dag.add_node("B", "img", {})
        dag.add_node("C", "vid", {})
        dag.add_edge("A", "B")
        dag.add_edge("B", "C")

        impact = dag.analyze_impact({"B"})
        assert "B" in impact["dirty_nodes"]
        assert "C" in impact["dirty_nodes"]
        assert "A" in impact["reusable_nodes"]
```

**交付物**:
- [ ] `tests/engine/test_dag.py` (>90% 覆盖)
- [ ] `tests/engine/test_fsm.py` (>90% 覆盖)
- [ ] `tests/core/test_store.py` (>80% 覆盖)

---

### Day 3 (周三) - 集成测试 & Mock

**任务**:
1. 创建 Mock 上游服务
   - Mock Kling API
   - Mock Runway API
   - Mock OpenAI API
2. 编写 Orchestrator 集成测试
   - `tests/engine/test_orchestrator_integration.py`
   - 测试完整 Pipeline 执行
   - 测试脏传播 Replay
3. 编写 Store 集成测试
   - 测试事务性
   - 测试并发访问

**Mock 示例**:
```python
# tests/mocks/upstream.py
import pytest
from unittest.mock import AsyncMock

class MockKlingClient:
    """Mock Kling API 客户端"""

    def __init__(self):
        self.jobs = {}

    async def create_job(self, params: dict) -> str:
        job_id = f"mock_{len(self.jobs)}"
        self.jobs[job_id] = {"status": "pending", "result": None}
        return job_id

    async def get_status(self, job_id: str) -> dict:
        job = self.jobs.get(job_id)
        if job:
            job["status"] = "completed"
            job["result"] = {"url": "mock://result.mp4"}
        return job

@pytest.fixture
def mock_kling():
    return MockKlingClient()
```

**交付物**:
- [ ] `tests/mocks/upstream.py`
- [ ] `tests/engine/test_orchestrator_integration.py`
- [ ] `tests/core/test_store_integration.py`

---

### Day 4 (周四) - CI/CD & 性能测试

**任务**:
1. 设置 GitHub Actions
   - `.github/workflows/test.yml`
   - 运行 pytest
   - 生成覆盖率报告
   - ruff lint 检查
2. 性能测试
   - `tests/performance/test_dag_performance.py`
   - 测试大规模 DAG (100+ nodes)
   - 测试并发执行
3. 压力测试
   - 测试高并发 Store 操作

**GitHub Actions 示例**:
```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - run: pip install -e ".[dev]"
      - run: pytest --cov=cine_mate --cov-report=xml --cov-report=html
      - run: ruff check .
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

**交付物**:
- [ ] `.github/workflows/test.yml`
- [ ] CI 运行成功
- [ ] 性能测试报告

---

### Day 5 (周五) - 测试报告 & Review

**任务**:
1. 生成测试报告
   - 覆盖率报告
   - 测试通过率
   - 缺陷统计
2. 为 hermes & copaw 的代码 Review
   - 关注测试可测性
   - 提出改进建议
3. 编写测试文档
   - `docs/testing_guide.md`
   - 测试最佳实践
4. Sprint Review Demo

**测试报告模板**:
```markdown
# Sprint 1 测试报告

## 覆盖率统计
| Module | Coverage | Status |
|--------|----------|--------|
| cine_mate/engine/dag.py | 95% | ✅ |
| cine_mate/engine/fsm.py | 98% | ✅ |
| cine_mate/core/store.py | 85% | ✅ |
| cine_mate/engine/orchestrator.py | 75% | ⚠️ |

## 测试结果
- 总测试数: 45
- 通过: 43
- 失败: 2
- 跳过: 0

## 发现的问题
1. [Issue #1] Orchestrator 异常处理不完善
2. [Issue #2] Store 并发访问可能有竞态条件

## 建议
1. 增加边界测试
2. 添加压力测试
```

**交付物**:
- [ ] 测试报告
- [ ] Code Review 反馈
- [ ] `docs/testing_guide.md`
- [ ] Sprint Review Demo

---

## 🤝 与团队的协作

### 协作点 1: 为 hermes 提供测试支持

**hermes 的任务**: AgentScope 集成

**你的支持**:
- 帮助设计 Agent 测试策略
- 为 DirectorAgent 编写测试
- Mock LLM 响应

**测试策略**:
```python
# tests/agents/test_director_agent.py
from unittest.mock import patch, MagicMock

class TestDirectorAgent:
    @patch("agentscope.agents.ReActAgent")
    async def test_parse_intent(self, mock_agent):
        # Mock LLM 返回固定 DAG
        mock_agent.return_value.chat.return_value = {...}

        agent = DirectorAgent()
        result = await agent.chat("Create a cyberpunk video")

        assert "nodes" in result
        assert len(result["nodes"]) > 0
```

### 协作点 2: 为 copaw 提供测试支持

**copaw 的任务**: Async Infra

**你的支持**:
- 为 JobQueue 编写测试
- Mock Redis
- 测试并发场景

### 协作点 3: Code Review (周四)

- Review hermes 的 Agent/Tools 代码
- Review copaw 的 Infra 代码
- 关注: 可测性、边界处理

---

## 📁 代码规范

### 文件结构
```
tests/
├── conftest.py              # 共享 fixture
├── test_cases_intent.json   # 意图测试用例 (已存在)
├── unit/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── test_store.py
│   │   └── test_models.py
│   └── engine/
│       ├── __init__.py
│       ├── test_dag.py
│       ├── test_fsm.py
│       └── test_orchestrator.py
├── integration/
│   ├── __init__.py
│   ├── test_orchestrator_integration.py
│   └── test_store_integration.py
├── mocks/
│   ├── __init__.py
│   └── upstream.py
└── performance/
    ├── __init__.py
    └── test_dag_performance.py
```

### 分支策略
```bash
# 你的工作分支
$ git checkout -b feature/sprint1-testing

# 提交规范
$ git commit -m "test(dag): add comprehensive DAG tests"
$ git commit -m "test(fsm): add state machine transition tests"
$ git commit -m "ci: add GitHub Actions workflow"
$ git commit -m "docs: add testing guide"

# 周五创建 PR
$ git push origin feature/sprint1-testing
```

### Commit Message 格式
```
type(scope): description

# Examples:
test(dag): add topology operation tests
test(fsm): add invalid transition tests
ci: add pytest and coverage workflow
docs(testing): add testing best practices guide
```

---

## 📚 你需要学习的

### 必学
1. **CineMate 架构**:
   - `docs/architecture.md`
   - `cine_mate/engine/` - 理解 DAG/FSM
   - `cine_mate/core/` - 理解 Store/Models

2. **pytest 进阶**:
   - fixtures
   - parametrized tests
   - async testing
   - mocks/patches

3. **测试模式**:
   - AAA (Arrange, Act, Assert)
   - Given-When-Then
   - Property-based testing (可选)

### 参考资源
- pytest 文档: https://docs.pytest.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- coverage.py: https://coverage.readthedocs.io/
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html

---

## 🚨 阻塞升级

如果你遇到以下情况，**立即升级到 PM**:

| 阻塞类型 | 升级条件 |
|----------|----------|
| 测试设计 | 无法为某模块设计测试 |
| 依赖问题 | 测试依赖复杂，无法 mock |
| 环境问题 | CI 环境无法运行测试 |
| 覆盖率低 | 某模块覆盖率 < 60%，需要设计建议 |
| 缺陷发现 | 发现严重 bug，需要立即修复 |

**升级方式**: 在项目群 @PM 或创建 GitHub Issue

---

## 💬 每日 Standup

请在每天结束时回复:

```markdown
**Name**: claude
**Date**: 2026-04-XX
**Yesterday**: (昨天完成了什么)
**Today**: (今天计划做什么)
**Blockers**: (有什么阻塞，没有就写 "None")
```

**示例**:
```markdown
**Name**: claude
**Date**: 2026-04-21
**Yesterday**: 搭建了测试框架，运行 pytest 成功
**Today**: 为 DAG 模块编写测试，目标 90% 覆盖
**Blockers**: Mock 上游 API 时遇到 async 问题，需要研究
```

---

## ✅ 验收检查清单

### 功能验收
- [ ] 测试框架运行成功
- [ ] DAG 测试 (>90% 覆盖)
- [ ] FSM 测试 (>90% 覆盖)
- [ ] Store 测试 (>80% 覆盖)
- [ ] Orchestrator 集成测试
- [ ] Mock 上游服务
- [ ] CI/CD 运行成功

### 代码质量
- [ ] 所有测试通过
- [ ] 整体覆盖率 > 80%
- [ ] 无 flaky tests
- [ ] 测试代码符合规范

### 文档验收
- [ ] 测试报告生成
- [ ] `docs/testing_guide.md`
- [ ] Code Review 反馈
- [ ] Sprint Review Demo

---

## 🎯 成功标准

**必须完成**:
- ✅ 测试框架搭建完成
- ✅ 核心模块单元测试 (>80% 覆盖)
- ✅ CI/CD 运行成功
- ✅ 测试报告

**争取完成**:
- ✅ 性能测试
- ✅ 集成测试
- ✅ 测试最佳实践文档

---

## 📞 联系方式

- **PM**: AI Assistant (我)
- **协作伙伴**: hermes (Agent/Gateway), copaw (Infra/Skill)
- **沟通**: 本对话 / GitHub Issues / Discord (待建立)

---

**Ready? Let's ensure quality from day one!** 🚀

> **"Quality is not an act, it is a habit."** — Aristotle

---

**Prepared by**: PM (AI Assistant)
**For**: claude
**Date**: 2026-04-20

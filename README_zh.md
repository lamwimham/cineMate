# CineMate 🎬

> **AI 视频创作操作系统**: 导演智能体 + 增量变更引擎

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-21%20files-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](tests/)
[![Architecture](https://img.shields.io/badge/architecture-4.1%2F5-blue.svg)](docs/PMO/)

**[🌐 English Version](README.md)** | **[📊 进度报告](docs/PMO/project_progress_report.md)** | **[📝 Sprint 3 路线图](docs/PMO/sprint3_roadmap.md)**

---

## 🎯 愿景

**让电影制作民主化，保护创意愿景，赋能创作者规模化生产——确保技术放大艺术性，而非取代它。**

CineMate 是一个 **AI 视频创作操作系统**，将软件工程实践引入视频创作。我们相信视频创作的未来不在于用自动化取代人类创意，而在于**通过智能工具放大创意潜力**。

不同于"一键生成"的黑盒工具（模糊创作过程）或复杂的节点式编辑器（需要技术专长），CineMate 是：

- **智能体驱动**: 导演智能体解析自然语言并编排整个流程——将愿景转化为执行，同时保护创意意图
- **版本控制**: 视频资产的 Git 式版本控制（"视频 Git"）——支持无风险实验
- **增量渲染**: 使用脏传播仅重新渲染变更节点——尊重创作时间和计算资源
- **云原生**: 本地优先执行 + 云脑编排——让创作者完全拥有资产

> "技术应该服务于故事，而非主导它。像管理代码一样管理视频创作——但保持电影制作的灵魂。"

---

## ✨ 核心特性

### 🎭 导演智能体 (Director Agent)
自然语言到视频流程。只需描述你的愿景：
```
"创建一个霓虹灯和雨水的赛博朋克视频"
"做成王家卫风格，慢动作"
"在广角镜头后添加产品特写"
```

智能体将你的意图转化为视频操作的 DAG（有向无环图）。

### 🔄 视频 Git (Video Git)
每次生成都是一个 commit。跟踪历史、分支实验、复用资产：

```python
# 运行 1: 初始生成
run_v1 = pipeline.run(prompt="赛博朋克城市")

# 运行 2: 修改灯光（从 v1 分支）
run_v2 = pipeline.run(
    prompt="更暖的灯光",
    parent_run_id=run_v1.run_id  # Git 式分支
)

# 仅变更节点重新渲染
# 未变更资产使用符号链接 (0 复制)
```

### ⚡ 增量引擎 (Incremental Engine)
使用 DAG 拓扑的智能脏传播：

```
原始：A → B → C → D
修改：B'

重新渲染：B' → C' → D'
复用：A (未变更)
```

### 🏗️ 异步基础设施 (Async Infrastructure)
生产级任务队列，支持长时间运行的视频操作：
- **JobQueue**: Redis 支持的任务队列，优先级支持
- **EventBus**: 发布/订阅实时通知
- **Workers**: 跨 GPU 集群的分布式执行

---

## 🏛️ 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户界面                                  │
│  CLI / Web / API                                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 导演智能体 (Director Agent)                 │
│  ReActAgent + 意图解析 → DAG 构建                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   核心引擎 (Core Engine)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     DAG      │  │     FSM      │  │ Orchestrator │      │
│  │  (拓扑结构)  │  │ (状态机)     │  │ (执行器)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│               异步基础设施 (Async Infra)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  JobQueue    │  │  EventBus    │  │   Workers    │      │
│  │  (Redis)     │  │ (Pub/Sub)    │  │  (RQ/Celery) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              提供者适配器 (Sprint 2 新增)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Kling      │  │   Runway     │  │   Mock       │      │
│  │  Provider    │  │  Provider    │  │  Provider    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  工厂 + 注册 + 健康检查 + 成本估算                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              上游 API                                        │
│  OpenAI · Kling AI · Runway ML · Luma AI · 本地 GPU         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 前置条件
- Python 3.11+
- Redis 6.0+ (用于异步基础设施)
- Docker (可选，用于容器化 Redis)

### 安装

```bash
# 克隆仓库
git clone https://github.com/lamwimham/cineMate.git
cd cineMate

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -e ".[dev]"

# 启动 Redis (使用 Docker)
docker-compose -f docker-compose.infra.yml up -d redis
```

### 验证安装

```bash
# 运行测试
pytest

# 预期输出:
# ===================== 121 passed in 3.42s ======================
# Coverage: core modules 96%+
```

---

## 📖 使用指南

### 1. 基础视频生成

```python
import asyncio
from cine_mate.agents.director_agent import DirectorAgent

async def main():
    # 初始化智能体
    agent = DirectorAgent(
        name="Director",
        model_config={"model_type": "openai", "model_name": "gpt-4"}
    )
    
    # 自然语言到视频
    result = await agent.chat(
        "创建一个 5 秒的赛博朋克城市场景，带霓虹灯"
    )
    
    print(f"Run ID: {result.run_id}")
    print(f"状态：{result.status}")

asyncio.run(main())
```

### 2. 视频 Git 工作流

```python
from cine_mate.core.store import Store
from cine_mate.engine.orchestrator import Orchestrator
from cine_mate.engine.dag import PipelineDAG

async def video_git_workflow():
    store = Store("./cinemate.db")
    await store.init_db()
    
    # 创建 DAG: 脚本 → 图像 → 视频
    dag = PipelineDAG()
    dag.add_node("script", "text_generation", {"prompt": "赛博朋克脚本"})
    dag.add_node("image", "image_generation", {"style": "neon"})
    dag.add_node("video", "video_generation", {"duration": 5})
    dag.add_edge("script", "image")
    dag.add_edge("image", "video")
    
    # 运行 1: 初始
    run1 = PipelineRun(run_id="run_001", dag_snapshot=dag.to_dict())
    orch1 = Orchestrator(store, run1, dag, executor_fn=mock_executor)
    await orch1.execute()
    
    # 运行 2: 修改图像节点（增量）
    dag.add_node("image", "image_generation", {"style": "film_noir"})
    run2 = PipelineRun(
        run_id="run_002",
        parent_run_id="run_001",  # Git 式父节点
        dag_snapshot=dag.to_dict()
    )
    
    # 仅 image → video 重新渲染
    # script 节点从 run_001 复用
    orch2 = Orchestrator(store, run2, dag, executor_fn=mock_executor)
    await orch2.execute()
```

### 3. 异步任务队列

```python
from cine_mate.infra.queue import JobQueue
from cine_mate.infra.event_bus import EventBus

async def async_pipeline():
    # 初始化基础设施
    event_bus = EventBus("redis://localhost:6379")
    await event_bus.connect()
    
    queue = JobQueue(
        redis_url="redis://localhost:6379",
        event_bus=event_bus
    )
    await queue.connect()
    
    # 提交任务
    job_id = await queue.submit_job(
        run_id="run_001",
        node_id="video_gen_01",
        job_type="image_to_video",
        params={
            "image_url": "https://...",
            "duration": 5,
            "motion_strength": 0.5
        },
        priority=1
    )
    
    # 订阅事件
    await event_bus.subscribe(
        "node_completed",
        lambda e: print(f"节点 {e.node_id} 完成!")
    )
```

---

## 🏗️ 项目结构

```
cineMate/
├── cine_mate/                 # 主包
│   ├── agents/                # 导演智能体 & 工具
│   │   ├── director_agent.py  # ReActAgent 实现
│   │   └── tools/             # 智能体工具 (EngineTools)
│   ├── adapters/              # 提供者适配器 (Sprint 2 新增)
│   │   ├── base.py            # BaseVideoProvider 抽象类
│   │   ├── factory.py         # 提供者注册 & 工厂
│   │   ├── kling_provider.py  # Kling AI 适配器
│   │   ├── runway_provider.py # Runway ML 适配器
│   │   └── mock_provider.py   # Mock 提供者 (测试用)
│   ├── config/                # 配置系统 (Sprint 2)
│   │   ├── models.py          # Pydantic 配置模型
│   │   ├── defaults.yaml      # 默认配置
│   │   └── loader.py          # 配置加载器
│   ├── core/                  # 核心数据模型 & 存储
│   │   ├── models.py          # Pydantic 模型 (Run, Node, Artifact)
│   │   └── store.py           # SQLite 存储层
│   ├── engine/                # 执行引擎
│   │   ├── dag.py             # DAG 拓扑 & 脏传播
│   │   ├── fsm.py             # 节点状态机
│   │   ├── orchestrator.py    # 流程执行
│   │   └── queue_integration.py # JobQueue-Engine 集成 (Sprint 3)
│   └── infra/                 # 异步基础设施
│       ├── queue.py           # JobQueue (Redis)
│       ├── event_bus.py       # EventBus (Pub/Sub)
│       ├── schemas.py         # 事件模型
│       └── worker.py          # RQ workers
├── tests/                     # 测试套件 (21 文件, 6,593 行)
│   ├── unit/                  # 单元测试 (13 文件)
│   │   ├── adapters/          # 提供者适配器测试
│   │   ├── core/              # Store 测试
│   │   ├── engine/            # DAG/FSM 测试
│   │   ├── infra/             # Queue/EventBus 测试
│   │   └── config/            # 配置加载器测试
│   ├── integration/           # 集成测试 (4 文件)
│   └── conftest.py            # Pytest fixtures
├── docs/                      # 文档
│   ├── architecture.md        # 系统架构
│   ├── adr/                   # 架构决策记录
│   ├── PMO/                   # 项目管理
│   │   ├── project_progress_report.md  # 整体进度
│   │   ├── sprint2_day4_summary.md     # Sprint 2 Day 4
│   │   └── sprint3_roadmap.md          # Sprint 3 路线图
│   └── testing/               # 测试报告
│       └── sprint2_coverage_report.md  # Sprint 2 覆盖率
├── prompts/                   # LLM 提示词
│   └── intent_v1.md           # 导演智能体提示词
├── .github/workflows/         # CI/CD (GitHub Actions)
│   └── test.yml               # pytest + coverage 工作流
├── pyproject.toml             # 项目配置
├── pytest.ini                 # 测试配置
└── docker-compose.infra.yml   # 本地 Redis 开发
```

---

## 🧪 测试

### 运行所有测试
```bash
pytest
```

### 运行覆盖率测试
```bash
pytest --cov=cine_mate --cov-report=html
open htmlcov/index.html
```

### 运行特定测试套件
```bash
pytest tests/unit/engine/test_dag.py -v
pytest tests/unit/engine/test_fsm.py -v
pytest tests/unit/core/test_store.py -v
```

### 当前测试状态
| 模块 | 测试数 | 覆盖率 | 状态 |
|------|--------|--------|------|
| DAG | 42 | 97% | ✅ |
| FSM | 42 | 97% | ✅ |
| Store | 35 | 90% | ✅ |
| Provider 适配器 | 53 | 86% | ✅ |
| Config Loader | 25 | 90% | ✅ |
| Queue Integration | 12 | 88% | ✅ |
| EventBus | 15 | 85% | ✅ |
| **总计** | **21 文件, 6,593 行** | **85%** | ✅ |

---

## 🤝 贡献指南

我们遵循结构化的开发流程：

### 分支命名
```
feature/sprint{N}-{description}
fix/{issue-id}-{description}
docs/{description}
```

### 提交规范
```
type(scope): description

类型:
- feat: 新功能
- fix: 修复
- docs: 文档
- test: 测试
- refactor: 重构

示例:
feat(agents): 添加导演智能体骨架
test(engine): 添加 DAG 脏传播测试
docs(adr): 添加任务队列决策记录
```

### 开发流程
1. 从 `main` 创建功能分支
2. 开发并编写测试
3. 提交 PR 并附描述
4. PM + 同行代码审查
5. 合并到 `main`

### 团队
- **hermes**: 智能体 & 网关负责人
- **copaw**: 基础设施 & 异步负责人
- **claude**: QA & 测试负责人
- **PM**: 项目管理 (AI 助手)

---

## 📋 路线图

### Sprint 1 (已完成) ✅
- [x] 核心引擎 (DAG, FSM, Orchestrator)
- [x] AgentScope 集成 (导演智能体)
- [x] 异步基础设施 (JobQueue, EventBus)
- [x] 测试框架 (21 文件, 6,593 行, 85% 覆盖率)
- [x] 事件驱动编排器 (node_completed 触发器)
- [x] 配置系统骨架 (多模型配置)

**结果**: ✅ **GO** - AgentScope + Engine 集成验证通过

### Sprint 2 (80% 完成) 🔄
**目标**: 提供者集成 + CI/CD + 测试覆盖率

| Day | 重点 | 状态 |
|-----|------|------|
| Day 1 | CI/CD GitHub Actions | ✅ 完成 |
| Day 2 | 配置系统 + 覆盖率扩展 | ✅ 完成 |
| Day 3 | 提供者适配器模式 (Kling, Runway, Mock) | ✅ 完成 |
| Day 4 | 集成测试 + 覆盖率报告 | ✅ 完成 |
| Day 5 | Sprint 评审演示 | ⏳ 待完成 |

**关键成果**:
- [x] 提供者适配器架构 (BaseVideoProvider, Factory, Registry)
- [x] Kling & Runway 提供者实现
- [x] Mock 提供者 (无需 API Key 测试)
- [x] CI/CD GitHub Actions (多 Python 版本)
- [x] 测试覆盖率: 85% (目标 >80%)
- [x] 架构健康评分: 4.1/5

### Sprint 3 (已启动) ⏳
**目标**: 架构改进 + 导演技能系统

| Part | 重点 | 状态 |
|------|------|------|
| Part 1/3 | JobQueue-Engine 集成层 | ✅ 完成 |
| Part 2/3 | EventBus 完整实现 | ⏳ 进行中 |
| Part 3/3 | Agents 依赖注入完善 | ⏳ 进行中 |

**规划**:
- [ ] 导演技能系统 (王家卫、赛博朋克风格)
- [ ] 多提供者路由 + 回退机制
- [ ] 生产强化

### 未来 Sprint
- [ ] Web UI (视频 Git 可视化)
- [ ] Human-in-the-Loop (HITL) 支持
- [ ] 生产环境部署

---

## 📚 文档

- [架构概览](docs/architecture.md)
- [异步接口规范](docs/architecture/async_interface.md)
- [ADR-001: 任务队列选型](docs/adr/ADR-001_job_queue.md)
- [智能体提示词模板](prompts/intent_v1.md)
- [项目进度报告](docs/PMO/project_progress_report.md)
- [Sprint 2 测试覆盖率报告](docs/testing/sprint2_coverage_report.md)
- [Sprint 3 路线图](docs/PMO/sprint3_roadmap.md)

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| 智能体框架 | AgentScope |
| API 框架 | FastAPI |
| 数据库 | SQLite (本地), PostgreSQL (云端) |
| 队列 | Redis + RQ |
| 事件 | Redis Pub/Sub |
| 测试 | pytest + pytest-asyncio |
| 代码检查 | ruff |

---

## 📄 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- 灵感来自 Git 的版本控制模型
- 智能体架构基于 ReAct 模式
- 事件驱动设计模式来自领域驱动设计 (DDD)

---

<p align="center">
  <strong>CineMate</strong> — 视频遇见工程
</p>

# hermes - Sprint 1 任务简报

> **Sprint**: 1 (2026-04-20 ~ 2026-04-27)  
> **Goal**: Validate AgentScope Integration & NL→DAG Intent Parsing  
> **Your Role**: 全栈开发工程师  
> **PM**: AI Assistant

---

## 🎯 本周目标

**验证 AgentScope 能否与 CineMate Engine 集成，将自然语言转换为 DAG 工作流。**

成功标准:
1. ✅ AgentScope 环境就绪，能运行 ReActAgent
2. ✅ DirectorAgent 基础类实现完成
3. ✅ Engine Toolkit 4 个工具实现
4. ✅ Agent + Toolkit + Engine 集成成功
5. ✅ 20 个 case 测试，准确率 >= 70%

---

## 📋 你的任务清单

### Day 1 (周一) - 环境准备

**任务**: 
1. 阅读 AgentScope 文档: https://doc.agentscope.io/
2. 安装 AgentScope: `pip install agentscope`
3. 跑通官方 EchoAgent Demo
4. 查看 M1 Engine 代码，理解 DAG 结构

**交付物**:
- [ ] AgentScope 成功安装，无冲突
- [ ] 本地可运行 EchoAgent Demo
- [ ] 理解 `cine_mate/engine/dag.py` 和 `orchestrator.py`

**参考**:
- Engine 代码: `cine_mate/engine/`
- Models: `cine_mate/core/models.py`

---

### Day 2 (周二) - 与 PM 协作

**PM 的任务** (你只需 Review):
- [ ] 设计 NL→DAG Prompt 模板
- [ ] 准备 20 个测试 case
- [ ] 手动测试 Prompt 准确率

**你的任务**:
- [ ] Review Prompt 设计，提出技术可行性意见
- [ ] 确认 DAG 结构是否符合 Engine 能力

---

### Day 3 (周三) - DirectorAgent 实现

**任务**:
1. 创建 `cine_mate/agents/__init__.py`
2. 实现 `cine_mate/agents/director_agent.py`

**DirectorAgent 基础类要求**:
```python
from agentscope.agents import ReActAgent

class DirectorAgent(ReActAgent):
    """
    CineMate Director Agent
    
    继承 ReActAgent，负责：
    1. 接收用户自然语言输入
    2. 解析意图并生成 DAG
    3. 调用 Engine Toolkit 执行操作
    """
    
    def __init__(self, name: str = "Director", **kwargs):
        super().__init__(
            name=name,
            system_prompt=SYSTEM_PROMPT,  # PM 提供的 Prompt
            **kwargs
        )
    
    async def chat(self, message: str) -> str:
        """主入口：接收用户消息，返回响应"""
        # TODO: 实现对话逻辑
        pass
```

**交付物**:
- [ ] `cine_mate/agents/director_agent.py` (骨架)
- [ ] 可实例化，能响应基础指令

---

### Day 4 (周四) - Engine Toolkit 实现

**任务**:
1. 创建 `cine_mate/agents/tools/engine_tools.py`
2. 实现 4 个核心工具

**Toolkit 要求**:
```python
from agentscope.tools import ToolBase

class EngineToolkit:
    """包装 Engine 操作，供 Agent 调用"""
    
    def create_pipeline(self, prompt: str) -> str:
        """
        创建新的 Pipeline Run
        Returns: run_id
        """
        pass
    
    def get_run_status(self, run_id: str) -> dict:
        """
        查询 Run 状态
        Returns: {"status": "running", "progress": 50%}
        """
        pass
    
    def modify_node(self, run_id: str, node_id: str, params: dict) -> bool:
        """
        修改节点参数，触发 Dirty Propagation
        Returns: True/False
        """
        pass
    
    def list_runs(self) -> list:
        """
        列出所有 Run
        Returns: [{"run_id": "xxx", "status": "completed"}]
        """
        pass
```

**集成到 Agent**:
```python
# director_agent.py
from .tools.engine_tools import EngineToolkit

class DirectorAgent(ReActAgent):
    def __init__(self, **kwargs):
        super().__init__(
            tools=EngineToolkit(),  # 注册 Toolkit
            **kwargs
        )
```

**交付物**:
- [ ] `cine_mate/agents/tools/engine_tools.py`
- [ ] Toolkit 可注册到 DirectorAgent
- [ ] 每个工具有单元测试

---

### Day 5 (周五) - 集成 & 测试

**任务**:
1. 集成 Agent + Toolkit + Engine
2. 运行 PM 提供的 20 个测试 case
3. 修复发现的问题

**测试流程**:
```python
# 测试脚本 (由 PM 提供或你自己写)
from cine_mate.agents.director_agent import DirectorAgent

async def test_case(input_text: str, expected_dag: dict):
    agent = DirectorAgent()
    result = await agent.chat(input_text)
    # 验证 result 是否符合 expected_dag
```

**交付物**:
- [ ] 端到端流程跑通
- [ ] 测试报告 (由 PM 统计准确率)
- [ ] 代码 Review 通过

---

## 📁 代码规范

### 文件结构
```
cine_mate/
├── agents/
│   ├── __init__.py          # 新创建
│   ├── director_agent.py    # Day 3 实现
│   └── tools/
│       ├── __init__.py      # 新创建
│       └── engine_tools.py  # Day 4 实现
```

### 分支策略
```
main (保护分支，不能 push)
  └── feature/sprint1-agent-scope (你的工作分支)
```

**Git 命令**:
```bash
# 1. 创建分支
git checkout -b feature/sprint1-agent-scope

# 2. 每天提交
git add .
git commit -m "feat(agents): add DirectorAgent skeleton"
git push origin feature/sprint1-agent-scope

# 3. 周五创建 PR (PM 会 Review)
git checkout main
git pull origin main
git checkout feature/sprint1-agent-scope
git rebase main
# 解决冲突后 push
git push origin feature/sprint1-agent-scope --force-with-lease
```

### Commit Message 格式
```
type(scope): description

# Examples:
feat(agents): add DirectorAgent skeleton
test(tools): add engine toolkit unit tests
docs(agents): update DirectorAgent docstrings
fix(tools): handle missing run_id in get_status
```

---

## 📚 参考文档

| 文档 | 路径 | 说明 |
|------|------|------|
| AgentScope Docs | https://doc.agentscope.io/ | 官方文档，必看 |
| 项目章程 | `docs/PMO/project_charter.md` | 协作规范 |
| 开发计划 v2 | `docs/PMO/development_plan_v2.md` | 完整路线图 |
| Sprint 1 详细 | `docs/PMO/sprint_1_hermes.md` | 任务看板 |
| Prompt 模板 | `prompts/intent_v1.md` | PM 准备的 Prompt |
| 测试用例 | `tests/test_cases_intent.json` | PM 准备的 20 个 case |
| M1 Engine | `cine_mate/engine/` | 需要集成的代码 |

---

## 🚨 阻塞升级

如果你遇到以下情况，**立即升级到 PM**:

| 阻塞类型 | 升级条件 |
|----------|----------|
| 技术选型 | 30 分钟无法决定 |
| 依赖冲突 | AgentScope 与现有库冲突，无法解决 |
| 架构问题 | Engine 接口设计不合理，需要修改 |
| 时间风险 | 某个任务超过预估 50% 时间 |
| 外部依赖 | 需要 PM 提供 Prompt/测试数据 |

**升级方式**: 在项目群 @PM 或创建 GitHub Discussion

---

## ✅ 验收检查清单

### 功能验收
- [ ] AgentScope 安装成功
- [ ] DirectorAgent 可实例化
- [ ] DirectorAgent 能接收用户输入
- [ ] Engine Toolkit 4 个工具可用
- [ ] Agent 能调用 Toolkit 创建 Pipeline
- [ ] Agent 能查询 Pipeline 状态

### 代码质量
- [ ] 单元测试覆盖率 >80%
- [ ] 代码通过 ruff 检查
- [ ] 类型注解完整 (mypy 无错)
- [ ] 文档字符串清晰

### 测试验收
- [ ] 20 个 case 测试完成
- [ ] 测试报告生成
- [ ] Go/No-Go 决策通过

---

## 💬 每日 Standup

请在每天结束时回复:

```markdown
**Date**: 2026-04-XX
**Yesterday**: (昨天完成了什么)
**Today**: (今天计划做什么)
**Blockers**: (有什么阻塞，没有就写 "None")
```

**示例**:
```markdown
**Date**: 2026-04-21
**Yesterday**: 安装了 AgentScope，成功运行 EchoAgent Demo
**Today**: 实现 DirectorAgent 基础类，开始编写 Engine Toolkit
**Blockers**: 无
```

---

## 🎯 成功标准 (Go/No-Go)

**Go Criteria** (满足任一即可):
- ✅ NL→DAG 准确率 >= 70%
- ✅ 或通过 "Agent 建议 + 用户确认" 可达 >= 90%

**No-Go Fallback**:
- ❌ 如果准确率 < 50%，降级为半自动模式
- ❌ Agent 仅提供表单建议，用户手动确认/调整

**周五决策**:
- PM 和 hermes 一起 Review 测试结果
- 决定是否继续当前路线或调整

---

## 📞 联系方式

- **PM**: AI Assistant (我)
- **沟通**: 本对话 / GitHub Issues / Discord (待建立)
- **文档**: GitHub Wiki / Notion (待建立)

---

**Ready? Let's build the future of video production!** 🚀

> **"The best way to predict the future is to implement it."** — David Heinemeier Hansson

---

**Prepared by**: PM (AI Assistant)  
**For**: hermes  
**Date**: 2026-04-20

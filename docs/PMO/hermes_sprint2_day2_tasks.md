# hermes Sprint 2 Day 2 任务通知

> **To**: hermes (Agent/Gateway 负责人)
> **From**: PM (AI Assistant)
> **Date**: 2026-04-23 (Sprint 2 Day 2)
> **Priority**: P0

---

## 📋 Day 2 任务清单

### 任务 1: 配置系统完整实现 (预计 4h)

**目标**: 完善 PR #11 配置骨架，实现环境变量覆盖 + API Key 验证

**当前状态** (PR #11):
- ✅ Pydantic 数据模型 (`models.py`)
- ✅ YAML 默认配置 (`defaults.yaml`)
- ⏳ 加载器骨架 (`loader.py`)
- ⏳ API Key 验证

---

### 任务 2: 真实 Agent 调用 (预计 6h)

**目标**: 取代 Mock Agent，接入 DashScope API

**验收标准**:
- DirectorAgent 使用真实 DashScope API
- `use_mock=False` 默认使用真实模型
- 错误处理 + 重试机制
- Demo 演示真实 Agent 调用

---

## 🔧 配置系统实现

### 1. 环境变量覆盖 (CINEMATE_*)

```python
# cine_mate/config/loader.py

import os
from pathlib import Path
from typing import Optional
import yaml

from cine_mate.config.models import CineMateConfig, ModelProfile

ENV_PREFIX = "CINEMATE_"

def load_config(config_path: Optional[str] = None) -> CineMateConfig:
    """
    Load CineMate configuration with priority:
    1. Environment variables (CINEMATE_*)
    2. User config file (cine_mate.yaml)
    3. Built-in defaults
    """
    # Load defaults
    defaults_path = Path(__file__).parent / "defaults.yaml"
    with open(defaults_path, "r") as f:
        raw = yaml.safe_load(f)

    # Load user config if exists
    user_config_path = config_path or Path.cwd() / "cine_mate.yaml"
    if user_config_path.exists():
        with open(user_config_path, "r") as f:
            user_raw = yaml.safe_load(f)
            raw = _merge_dicts(raw, user_raw)

    # Apply env overrides
    raw = _apply_env_overrides(raw)

    # Validate API keys
    config = CineMateConfig(**raw)
    validate_api_keys(config)

    return config

def _apply_env_overrides(raw: dict) -> dict:
    """Apply environment variable overrides."""
    env_mappings = {
        "CINEMATE_LLM_MODEL": ("models", "llm", "primary", "model_name"),
        "CINEMATE_LLM_API_KEY": ("models", "llm", "primary", "api_key"),
        "CINEMATE_REDIS_URL": ("infra", "redis_url"),
        "CINEMATE_LOG_LEVEL": ("app", "log_level"),
    }

    for env_key, path in env_mappings.items():
        env_value = os.getenv(env_key)
        if env_value:
            _set_nested(raw, path, env_value)

    return raw

def _set_nested(d: dict, path: tuple, value: str):
    """Set nested dict value."""
    for key in path[:-1]:
        d = d.setdefault(key, {})
    d[path[-1]] = value
```

---

### 2. API Key 验证

```python
# cine_mate/config/validator.py

import os
from typing import List, Tuple

from cine_mate.config.models import CineMateConfig, ModelProfile

def validate_api_keys(config: CineMateConfig) -> List[Tuple[str, bool]]:
    """
    Validate API keys at startup.
    Returns list of (provider, is_valid) tuples.
    """
    results = []

    # Check DashScope API Key
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    if dashscope_key:
        results.append(("dashscope_qwen", True))
    else:
        results.append(("dashscope_qwen", False))

    # Check other providers
    for provider_env in ["FLUX_API_KEY", "KLING_API_KEY", "RUNWAY_API_KEY"]:
        key = os.getenv(provider_env)
        results.append((provider_env.replace("_API_KEY", "").lower(), bool(key)))

    # Log missing keys
    missing = [p for p, valid in results if not valid]
    if missing:
        print(f"⚠️ Missing API keys: {missing}")

    return results
```

---

## 🔧 真实 Agent 调用实现

### 1. DirectorAgent 真实调用

```python
# cine_mate/agents/director_agent.py

class DirectorAgent(ReActAgent):
    def __init__(
        self,
        name: str = "Director",
        model_name: str = "qwen-max",
        api_key: Optional[str] = None,
        engine_tools: Optional[EngineTools] = None,
        use_mock: bool = False,
        model=None
    ):
        if use_mock:
            model = MockChatModel()
        elif model is not None:
            pass  # Use injected model
        else:
            # Real DashScope API call
            model = DashScopeChatModel(
                model_name=model_name,
                api_key=api_key or os.getenv("DASHSCOPE_API_KEY"),
            )

            # Validate API key
            if not model.api_key:
                raise ValueError("DASHSCOPE_API_KEY not set. Please set env var or pass api_key param.")
```

---

### 2. Demo 真实调用脚本

```python
# scripts/demo_real_agent.py

import asyncio
import os
from cine_mate.agents.director_agent import DirectorAgent
from cine_mate.agents.tools.engine_tools import EngineTools
from cine_mate.infra.queue import JobQueue
from cine_mate.infra.event_bus import EventBus

async def demo_real_agent():
    # Validate API key
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ DASHSCOPE_API_KEY not set")
        return

    # Setup infrastructure
    event_bus = EventBus("redis://localhost:6379")
    await event_bus.connect()

    queue = JobQueue(
        redis_url="redis://localhost:6379",
        event_bus=event_bus
    )
    await queue.connect()

    tools = EngineTools(job_queue=queue)
    await tools.init_db()

    # Create DirectorAgent with real API
    agent = DirectorAgent(
        name="Director",
        model_name="qwen-max",
        engine_tools=tools,
        use_mock=False  # Real API call
    )

    # Test call
    result = await agent.chat("Create a 5-second cyberpunk city scene")
    print(f"✅ Result: {result}")

asyncio.run(demo_real_agent())
```

---

## ✅ 验收标准

### 配置系统

- [ ] 环境变量覆盖实现 (CINEMATE_*)
- [ ] API Key 验证实现
- [ ] 用户配置文件加载 (cine_mate.yaml)
- [ ] 配置优先级正确 (env > user > defaults)
- [ ] 单元测试通过

### 真实 Agent 调用

- [ ] DirectorAgent 使用真实 DashScope API
- [ ] API Key 缺失时抛出 ValueError
- [ ] 错误处理 + 重试机制
- [ ] Demo 脚本运行成功
- [ ] `use_mock=False` 默认行为

---

## 📝 提交要求

### PR 格式

```
Title: feat(config): Complete config system + real Agent call

Body:
- Implement env variable override (CINEMATE_*)
- Implement API Key validation at startup
- Implement user config file loading
- DirectorAgent real DashScope API call
- Demo script for real Agent

Refs: PR #11 (config skeleton)
Closes Sprint 2 Day 2 tasks
```

---

## ⏰ 时间安排

| 时间 | 任务 |
|------|------|
| 09:00 - 12:00 | 配置系统完整实现 |
| 14:00 - 17:00 | 真实 Agent 调用 |
| 17:00 | Daily Standup |

---

## 📞 协作

- **Standup**: 17:00 汇报进度
- **如有阻塞**: 与 copaw 对齐接口

---

**签名**: PM (AI Assistant)
**日期**: 2026-04-23
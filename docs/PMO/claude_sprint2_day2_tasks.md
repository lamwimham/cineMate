# claude Sprint 2 Day 2 任务通知

> **To**: claude (QA/Testing 负责人)
> **From**: PM (AI Assistant)
> **Date**: 2026-04-23 (Sprint 2 Day 2)
> **Priority**: P1

---

## 📋 Day 2 任务清单

### 任务 1: 测试覆盖率提升 >90% (预计 4h)

**目标**: 提升 Sprint 2 测试覆盖率至 >90%

**当前状态**:
- ✅ 21 files, 2007 lines, 77% coverage
- ⏳ 目标: >90%

---

### 任务 2: 配置系统测试 (预计 2h)

**目标**: 为 hermes 配置系统补充单元测试

**验收标准**:
- `test_config_loader.py` - 环境变量覆盖测试
- `test_config_validator.py` - API Key 验证测试
- `test_config_integration.py` - 配置加载集成测试

---

## 🔧 测试覆盖率提升

### 优先补充模块

| 模块 | 当前覆盖率 | 目标 | 优先级 |
|------|-----------|------|--------|
| `cine_mate/config/` | 0% | 100% | P0 |
| `cine_mate/agents/` | - | 80% | P1 |
| `cine_mate/engine/orchestrator.py` | - | 90% | P1 |
| `cine_mate/infra/event_bus.py` | 77% | 95% | P1 |

---

### 测试文件规划

```
tests/
├── unit/
│   ├── config/
│   │   ├── test_loader.py          # 环境变量覆盖测试
│   │   ├── test_validator.py       # API Key 验证测试
│   │   └── test_models.py          # Pydantic 模型测试
│   ├── agents/
│   │   ├── test_director_agent.py  # DirectorAgent 测试
│   │   └── test_engine_tools.py    # EngineTools 测试
│   └── engine/
│       └── test_orchestrator_events.py  # Orchestrator 事件测试
└── integration/
    └── test_config_integration.py  # 配置加载集成测试
```

---

## 🔧 测试代码示例

### 1. 配置加载测试

```python
# tests/unit/config/test_loader.py

import os
import pytest
from pathlib import Path
from cine_mate.config.loader import load_config, _apply_env_overrides
from cine_mate.config.models import CineMateConfig

def test_load_defaults():
    """Test loading default configuration."""
    config = load_config()
    assert config.models.llm.primary.model_name == "qwen-max"
    assert config.infra.redis_url == "redis://localhost:6379"

def test_env_override_llm_model():
    """Test environment variable override for LLM model."""
    os.environ["CINEMATE_LLM_MODEL"] = "qwen-plus"

    raw = {"models": {"llm": {"primary": {"model_name": "qwen-max"}}}}
    raw = _apply_env_overrides(raw)

    assert raw["models"]["llm"]["primary"]["model_name"] == "qwen-plus"

    del os.environ["CINEMATE_LLM_MODEL"]

def test_env_override_redis_url():
    """Test environment variable override for Redis URL."""
    os.environ["CINEMATE_REDIS_URL"] = "redis://custom:6379"

    config = load_config()
    assert config.infra.redis_url == "redis://custom:6379"

    del os.environ["CINEMATE_REDIS_URL"]
```

---

### 2. API Key 验证测试

```python
# tests/unit/config/test_validator.py

import os
import pytest
from cine_mate.config.validator import validate_api_keys
from cine_mate.config.loader import load_config

def test_validate_dashscope_key_present():
    """Test DashScope API key validation when present."""
    os.environ["DASHSCOPE_API_KEY"] = "test_key"

    config = load_config()
    results = validate_api_keys(config)

    dashscope_result = [r for r in results if r[0] == "dashscope_qwen"][0]
    assert dashscope_result[1] is True

    del os.environ["DASHSCOPE_API_KEY"]

def test_validate_dashscope_key_missing():
    """Test DashScope API key validation when missing."""
    # Ensure key is not set
    if "DASHSCOPE_API_KEY" in os.environ:
        del os.environ["DASHSCOPE_API_KEY"]

    config = load_config()
    results = validate_api_keys(config)

    dashscope_result = [r for r in results if r[0] == "dashscope_qwen"][0]
    assert dashscope_result[1] is False

def test_validate_multiple_keys():
    """Test validation of multiple API keys."""
    os.environ["DASHSCOPE_API_KEY"] = "test_key"
    os.environ["KLING_API_KEY"] = "test_key"

    config = load_config()
    results = validate_api_keys(config)

    valid_count = sum(1 for _, valid in results if valid)
    assert valid_count >= 2

    del os.environ["DASHSCOPE_API_KEY"]
    del os.environ["KLING_API_KEY"]
```

---

### 3. DirectorAgent 测试

```python
# tests/unit/agents/test_director_agent.py

import pytest
from cine_mate.agents.director_agent import DirectorAgent, MockChatModel

def test_director_agent_mock_mode():
    """Test DirectorAgent in mock mode."""
    agent = DirectorAgent(name="Test", use_mock=True)
    assert isinstance(agent.model, MockChatModel)

def test_director_agent_injected_model():
    """Test DirectorAgent with injected model."""
    mock_model = MockChatModel()
    agent = DirectorAgent(name="Test", model=mock_model)
    assert agent.model == mock_model

def test_director_agent_missing_api_key():
    """Test DirectorAgent raises error when API key missing."""
    import os
    if "DASHSCOPE_API_KEY" in os.environ:
        del os.environ["DASHSCOPE_API_KEY"]

    with pytest.raises(ValueError, match="DASHSCOPE_API_KEY not set"):
        DirectorAgent(name="Test", use_mock=False)
```

---

## ✅ 验收标准

- [ ] `test_loader.py` 环境变量覆盖测试通过
- [ ] `test_validator.py` API Key 验证测试通过
- [ ] `test_director_agent.py` DirectorAgent 测试通过
- [ ] 测试覆盖率 >90%
- [ ] CI/CD GitHub Actions 测试通过

---

## 📝 提交要求

### PR 格式

```
Title: test(config): Add unit tests for config system

Body:
- Add test_loader.py (env override tests)
- Add test_validator.py (API key validation tests)
- Add test_director_agent.py (DirectorAgent tests)
- Coverage increased to >90%

Refs: PR #11 (config skeleton), PR #12 (DirectorAgent fix)
```

---

## ⏰ 时间安排

| 时间 | 任务 |
|------|------|
| 09:00 - 12:00 | 测试覆盖率提升 (>90%) |
| 14:00 - 16:00 | 配置系统测试 |
| 17:00 | Daily Standup |

---

## 📞 协作

- **Standup**: 17:00 汇报进度
- **如有阻塞**: 与 hermes 对齐测试需求

---

**签名**: PM (AI Assistant)
**日期**: 2026-04-23
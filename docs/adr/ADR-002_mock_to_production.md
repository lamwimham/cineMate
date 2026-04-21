# ADR-002: Mock Services to Production Migration

> **Status**: Active  
> **Date**: 2026-04-23  
> **Author**: claude (QA/Testing)  
> **Deciders**: PM, hermes, copaw  
> **Related**: PR #5, `tests/mocks/upstream.py`

---

## Context

Sprint 1 期间，claude 实现了 Mock 上游服务（Kling/Runway/OpenAI）用于集成测试。这些 Mock 服务当前位于 `tests/mocks/` 目录下，支持本地开发和测试，但**不能直接用于生产环境**。

---

## Mock 服务清单

### 当前实现

| 文件 | Mock 服务 | 生产替代 | 状态 |
|------|-----------|----------|------|
| `tests/mocks/upstream.py` | `MockKlingClient` | `KlingClient` (真实 API) | ⏳ Mock |
| `tests/mocks/upstream.py` | `MockRunwayClient` | `RunwayClient` (真实 API) | ⏳ Mock |
| `tests/mocks/upstream.py` | `MockOpenAIClient` | `OpenAIClient` (真实 API) | ⏳ Mock |
| `tests/mocks/upstream.py` | `MockS3Storage` | `S3Storage` / `R2Storage` | ⏳ Mock |

### Mock 行为特征

| 特征 | Mock 实现 | 生产要求 | 影响 |
|------|-----------|----------|------|
| **延迟** | 固定 100-500ms | 真实 API 延迟 (2-30s) | 测试不充分 |
| **成功率** | 可配置，默认 95% | 真实成功率 (~90%) | 错误处理未充分测试 |
| **Cost** | 模拟值 $0.01-0.05 | 真实计费 | 计费逻辑未验证 |
| **并发** | 无限制 | API Rate Limit | 并发控制缺失 |
| **文件存储** | 本地临时文件 | S3/R2/本地存储 | 存储策略未验证 |
| **回调/Webhook** | 同步返回 | 异步回调 | 异步流程未测试 |

---

## 生产迁移路线图

### Phase 1: Sprint 2 (M3 - Cloud Gateway)

**目标**: 实现真实 API Client 骨架

#### Task 1: 真实 API Client 接口设计

**文件**: `cine_mate/gateway/clients/__init__.py`

```python
# 抽象基类，与 Mock 保持兼容
from abc import ABC, abstractmethod
from typing import Dict, Any

class UpstreamClient(ABC):
    """Base class for upstream API clients"""
    
    @abstractmethod
    async def create_job(self, params: Dict[str, Any]) -> str:
        """Create a job and return job_id"""
        pass
    
    @abstractmethod
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status and result"""
        pass
    
    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        pass
```

#### Task 2: Kling API Client (Real)

**文件**: `cine_mate/gateway/clients/kling.py`

```python
import httpx
from . import UpstreamClient

class KlingClient(UpstreamClient):
    """
    Production Kling API Client
    
    FIXME: Current implementation uses Mock for testing
    TODO: Replace with real API calls
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.klingai.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60.0
        )
    
    async def create_job(self, params: Dict[str, Any]) -> str:
        """Create image/video generation job"""
        # TODO: Replace Mock with real API
        # Current: return await self._mock_create_job(params)
        # Target: 
        # response = await self.client.post("/v1/images/generations", json=params)
        # return response.json()["data"]["task_id"]
        pass
```

#### Task 3: 配置驱动的 Client 选择

**文件**: `cine_mate/config.py`

```python
from enum import Enum

class UpstreamMode(str, Enum):
    """Upstream client mode"""
    MOCK = "mock"          # Sprint 1: 本地测试
    SANDBOX = "sandbox"    # Sprint 2: 沙盒环境 (有限调用)
    PRODUCTION = "production"  # Sprint 3+: 真实生产环境

UPSTREAM_CONFIG = {
    "mode": UpstreamMode.MOCK,  # FIXME: Change to PRODUCTION for release
    "clients": {
        "kling": {
            "mock": "tests.mocks.upstream:MockKlingClient",
            "sandbox": "cine_mate.gateway.clients.kling:KlingSandboxClient",
            "production": "cine_mate.gateway.clients.kling:KlingClient",
        },
        "runway": {...},
        "openai": {...},
    }
}
```

#### Task 4: 替换检查清单

**文件**: `docs/PRODUCTION_READINESS.md`

| 检查项 | Sprint 2 | Sprint 3 | Sprint 4 |
|--------|----------|----------|----------|
| API Key 管理 | ⏳ Config | ✅ Vault | ✅ Rotation |
| Rate Limit 处理 | ⏳ Client | ✅ Gateway | ✅ Adaptive |
| 错误重试策略 | ⏳ Basic | ✅ Exponential | ✅ Circuit Breaker |
| 成本估算 | ⏳ Mock | ✅ Real-time | ✅ Budget Alert |
| 异步回调 | ⏳ Polling | ✅ Webhook | ✅ Event Bus |
| 数据加密 | ⏳ None | ✅ TLS | ✅ E2E |

### Phase 2: Sprint 3 (M3 - Production Hardening)

**目标**: 沙盒环境测试 + 错误处理完善

#### 关键任务

1. **Sandbox Environment**
   - 使用 Kling/Runway 沙盒 API (有限免费调用)
   - 验证真实延迟和错误模式
   - 调整超时和重试策略

2. **Error Handling**
   ```python
   # Production-grade error handling
   class UpstreamError(Exception):
       """Base upstream error"""
       
   class RateLimitError(UpstreamError):
       """429 Too Many Requests"""
       retry_after: int  # seconds
       
   class InsufficientCreditsError(UpstreamError):
       """402 Payment Required"""
       required: float
       available: float
   ```

3. **Cost Tracking**
   - 集成真实计费 API
   - 实现成本预估 (pre-flight)
   - 预算告警机制

### Phase 3: Sprint 4 (Production)

**目标**: 全量生产切换

#### 发布检查清单

- [ ] 所有 Mock 调用替换为真实 API
- [ ] API Key 安全存储 (Vault/AWS Secrets Manager)
- [ ] Rate Limit 配置验证
- [ ] 成本监控 Dashboard
- [ ] 熔断降级策略生效
- [ ] 数据备份策略

---

## 代码标记

### Mock 使用点标记

在代码中使用 `# FIXME(ADR-002)` 标记需要替换的地方：

```python
# cine_mate/infra/worker.py

async def execute_job(self, job: Dict[str, Any]):
    """Execute a job using upstream provider"""
    
    provider = job["upstream_provider"]
    
    # FIXME(ADR-002): Using Mock for Sprint 1 testing
    # Replace with real client in Sprint 2
    if provider == "kling":
        from tests.mocks.upstream import MockKlingClient
        client = MockKlingClient()
    elif provider == "runway":
        from tests.mocks.upstream import MockRunwayClient
        client = MockRunwayClient()
    
    # Target (Sprint 2+):
    # from cine_mate.gateway.clients import get_client
    # client = get_client(provider)
    
    return await client.execute(job["params"])
```

### 搜索命令

查找所有需要修复的 Mock 使用点：

```bash
# Find all FIXME(ADR-002) markers
grep -r "FIXME(ADR-002)" cine_mate/

# Find Mock imports outside tests/
grep -r "from tests.mocks" cine_mate/ --include="*.py"

# Find Mock usage in production code
grep -r "MockKling\|MockRunway\|MockOpenAI" cine_mate/ --include="*.py"
```

---

## 风险评估

### 当前风险 (Sprint 1)

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Mock 未覆盖真实错误场景 | 高 | Sprint 2 添加错误注入测试 |
| Mock 延迟不真实 | 中 | Sprint 2 使用延迟注入 |
| 计费逻辑未验证 | 高 | Sprint 2 沙盒环境验证 |

### 迁移风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| API Key 泄露 | 高 | 使用 Vault，禁止硬编码 |
| Rate Limit 触发 | 中 | 实现 Backoff + Queue |
| 成本超支 | 高 | Budget Alert + 硬限制 |

---

## 相关文件

| 文件 | 用途 | 生产替换 |
|------|------|----------|
| `tests/mocks/upstream.py` | Mock 实现 | N/A (保持测试用) |
| `tests/mocks/test_upstream.py` | Mock 测试 | N/A (保持测试用) |
| `cine_mate/infra/worker.py` | 使用 Mock | `cine_mate/gateway/clients/*.py` |
| `cine_mate/agents/tools/engine_tools.py` | 使用 Mock | `cine_mate/gateway/router.py` |

---

## 决策记录

### 决策 1: 保留 Mock 服务位置

- **决策**: Mock 服务保留在 `tests/mocks/`，不移动到生产代码
- **理由**: 明确区分测试和生产代码，防止误用
- **影响**: 生产代码需要通过配置动态加载 Client

### 决策 2: 配置驱动的 Client 选择

- **决策**: 使用 `UPSTREAM_CONFIG["mode"]` 切换 Mock/沙盒/生产
- **理由**: 支持渐进式迁移，便于测试
- **影响**: 需要配置管理系统支持

### 决策 3: FIXME(ADR-002) 标记约定

- **决策**: 所有 Mock 使用点标记 FIXME(ADR-002)
- **理由**: 便于搜索和跟踪
- **影响**: 代码审查时必须检查

---

## 附录: Mock 服务详情

### MockKlingClient

```python
class MockKlingClient:
    """Mock Kling API for Sprint 1 testing"""
    
    async def create_image_job(self, params: Dict[str, Any]) -> str:
        """Create image generation job"""
        # FIXME(ADR-002): Replace with real Kling API call
        await asyncio.sleep(0.5)  # Mock latency
        return f"mock_kling_img_{uuid.uuid4().hex[:12]}"
    
    async def create_video_job(self, params: Dict[str, Any]) -> str:
        """Create video generation job"""
        # FIXME(ADR-002): Replace with real Kling API call
        await asyncio.sleep(2.0)  # Mock latency
        return f"mock_kling_vid_{uuid.uuid4().hex[:12]}"
```

### 生产 KlingClient

```python
class KlingClient:
    """Production Kling API Client (TODO: Sprint 2)"""
    
    async def create_image_job(self, params: Dict[str, Any]) -> str:
        """Create image generation job via Kling API"""
        # TODO(ADR-002): Implement real API call
        # POST https://api.klingai.com/v1/images/generations
        pass
```

---

**Last Updated**: 2026-04-23  
**Next Review**: Sprint 2 Planning (2026-04-28)

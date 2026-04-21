# Video Generation Provider API 调研报告

> **作者**: copaw (Infra & Skill 负责人)  
> **日期**: 2026-04-23  
> **Sprint**: 2 Day 2  
> **目的**: 为 CineMate 选择最佳的视频生成 Provider 适配器

---

## 📊 执行摘要

| Provider | API 价格 | 视频质量 | 文档完整度 | 推荐度 |
|----------|----------|----------|------------|--------|
| **Kling 2.x/3.0** | $0.075/s | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 首选 |
| **Runway Gen-4** | $0.05/s | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 备选 |
| **Luma Dream Machine** | $0.10/s | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⚠️ 次选 |

**推荐**: **Kling 2.x/3.0** 作为首选 Provider (性价比高，质量优秀)

---

## 1. Kling AI API

### 1.1 基本信息

| 项目 | 详情 |
|------|------|
| 提供商 | ByteDance |
| 当前版本 | Kling 3.0 / Kling O3 |
| API 入口 | WaveSpeedAI / 官方 API |
| 文档 | https://wavespeed.ai/blog/posts/kling-2-0-complete-guide-2026/ |

### 1.2 定价 (2026 年 4 月)

| 模式 | 价格 | 备注 |
|------|------|------|
| Text-to-Video | $0.075/s | 基础生成 |
| Image-to-Video | $0.075/s | 参考图生成 |
| Kling O3 (高级) | $0.224/s | 多镜头支持 |

**示例成本**:
- 10 秒 720p 视频: $0.75
- 60 秒视频: $4.50

### 1.3 API 端点

```
POST https://api.wavespeed.ai/v1/video/generation
Headers:
  Authorization: Bearer {API_KEY}
  Content-Type: application/json

Body:
{
  "model": "kling-2.0",
  "prompt": "A cinematic shot of...",
  "duration": 10,
  "resolution": "720p",
  "mode": "text_to_video"
}

Response:
{
  "job_id": "job_xxx",
  "status": "processing",
  "estimated_time": 60
}
```

### 1.4 支持功能

- ✅ Text-to-Video
- ✅ Image-to-Video
- ✅ Video-to-Video (编辑)
- ✅ 最长 10 秒/次生成
- ✅ 商业使用许可
- ⚠️ 音频支持 (需确认)

### 1.5 适配器实现建议

```python
# cine_mate/skills/providers/kling_provider.py

class KlingProvider(BaseVideoProvider):
    """Kling AI Video Generation Provider"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.wavespeed.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = "kling-2.0"
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 10,
        resolution: str = "720p",
        image_url: Optional[str] = None
    ) -> VideoGenerationResult:
        # 实现 Kling API 调用
        pass
    
    def estimate_cost(self, duration: int) -> float:
        return duration * 0.075  # $0.075/s
```

---

## 2. Runway Gen-4 API

### 2.1 基本信息

| 项目 | 详情 |
|------|------|
| 提供商 | Runway ML |
| 当前版本 | Gen-4 Turbo |
| API 入口 | 官方 API |
| 文档 | https://runwayml.com/api/docs |

### 2.2 定价 (2026 年 4 月)

| 模式 | 价格 | 备注 |
|------|------|------|
| Gen-4 Turbo API | $0.05/s | 最具性价比 |
| Unlimited Plan | $76/month | 包含 Explore Mode |
| Standard Plan | $15/user/month | 625 credits/month |

**示例成本**:
- 10 秒 720p 视频: $0.50
- 60 秒视频: $3.00

### 2.3 API 端点

```
POST https://api.runwayml.com/v1/video/generate
Headers:
  Authorization: Bearer {API_KEY}
  Content-Type: application/json

Body:
{
  "model": "gen-4-turbo",
  "prompt": "A cinematic shot of...",
  "duration_seconds": 10,
  "resolution": "720p"
}

Response:
{
  "id": "runway_xxx",
  "status": "processing",
  "output_url": "https://..."
}
```

### 2.4 支持功能

- ✅ Text-to-Video
- ✅ Image-to-Video
- ✅ Video Editing
- ✅ 多种分辨率
- ✅ 商业使用许可
- ✅ 完整 API 文档

### 2.5 适配器实现建议

```python
# cine_mate/skills/providers/runway_provider.py

class RunwayProvider(BaseVideoProvider):
    """Runway Gen-4 Video Generation Provider"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.runwayml.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = "gen-4-turbo"
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 10,
        resolution: str = "720p"
    ) -> VideoGenerationResult:
        # 实现 Runway API 调用
        pass
    
    def estimate_cost(self, duration: int) -> float:
        return duration * 0.05  # $0.05/s
```

---

## 3. Luma Dream Machine API

### 3.1 基本信息

| 项目 | 详情 |
|------|------|
| 提供商 | Luma AI |
| 当前版本 | Dream Machine (Ray3) |
| API 入口 | PiAPI / 官方 API |
| 文档 | https://piapi.ai/blogs/luma-ai-dream-machine-intro |

### 3.2 定价 (2026 年 4 月)

| 模式 | 价格 | 备注 |
|------|------|------|
| Standard | $0.10/s | 基础生成 |
| Pro (带音频) | $0.20/s | 高级功能 |
| Free Plan | 有限额度 | 测试用 |

**示例成本**:
- 10 秒 720p 视频: $1.00
- 60 秒视频: $6.00

### 3.3 API 端点

```
POST https://api.piapi.ai/v1/luma/generate
Headers:
  Authorization: Bearer {API_KEY}
  Content-Type: application/json

Body:
{
  "model": "dream-machine",
  "prompt": "A cinematic shot of...",
  "duration": 10
}

Response:
{
  "task_id": "luma_xxx",
  "status": "queued",
  "video_url": "https://..."
}
```

### 3.4 支持功能

- ✅ Text-to-Video
- ✅ Image-to-Video
- ✅ 3D 生成 (Genie)
- ⚠️ API 访问受限
- ✅ 商业使用许可
- ⚠️ 文档不完整

### 3.5 适配器实现建议

```python
# cine_mate/skills/providers/luma_provider.py

class LumaProvider(BaseVideoProvider):
    """Luma Dream Machine Video Generation Provider"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.piapi.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = "dream-machine"
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 10
    ) -> VideoGenerationResult:
        # 实现 Luma API 调用
        pass
    
    def estimate_cost(self, duration: int) -> float:
        return duration * 0.10  # $0.10/s
```

---

## 4. 对比总结

### 4.1 价格对比

| Provider | 10 秒视频 | 60 秒视频 | 性价比 |
|----------|-----------|-----------|--------|
| Runway Gen-4 | $0.50 | $3.00 | ⭐⭐⭐⭐⭐ |
| Kling 2.x | $0.75 | $4.50 | ⭐⭐⭐⭐ |
| Luma Dream | $1.00 | $6.00 | ⭐⭐⭐ |

### 4.2 功能对比

| 功能 | Kling | Runway | Luma |
|------|-------|--------|------|
| Text-to-Video | ✅ | ✅ | ✅ |
| Image-to-Video | ✅ | ✅ | ✅ |
| Video Editing | ✅ | ✅ | ⚠️ |
| 音频支持 | ⚠️ | ✅ | ✅ |
| API 文档 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 商业许可 | ✅ | ✅ | ✅ |

### 4.3 推荐方案

**首选**: **Kling 2.x**
- 理由：性价比高，视频质量优秀，ByteDance 背书
- 适用场景：大部分视频生成需求

**备选**: **Runway Gen-4**
- 理由：价格最低，文档完整，功能丰富
- 适用场景：预算敏感项目

**不推荐**: **Luma Dream Machine**
- 理由：价格最高，API 访问受限
- 适用场景：特殊 3D 需求

---

## 5. CineMate 适配器设计

### 5.1 基类设计

```python
# cine_mate/skills/providers/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class VideoGenerationResult:
    job_id: str
    status: str
    video_url: Optional[str]
    cost: float
    duration: int

class BaseVideoProvider(ABC):
    """Base class for all video generation providers"""
    
    @abstractmethod
    async def generate_video(self, prompt: str, **kwargs) -> VideoGenerationResult:
        pass
    
    @abstractmethod
    def estimate_cost(self, duration: int) -> float:
        pass
    
    @abstractmethod
    async def check_status(self, job_id: str) -> str:
        pass
```

### 5.2 Provider 工厂

```python
# cine_mate/skills/providers/factory.py

from typing import Type
from .base import BaseVideoProvider
from .kling_provider import KlingProvider
from .runway_provider import RunwayProvider
from .luma_provider import LumaProvider

PROVIDER_REGISTRY = {
    "kling": KlingProvider,
    "runway": RunwayProvider,
    "luma": LumaProvider,
}

def get_provider(provider_name: str, api_key: str) -> BaseVideoProvider:
    """Factory function to get provider instance"""
    provider_class = PROVIDER_REGISTRY.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")
    return provider_class(api_key)
```

### 5.3 与 JobQueue 集成

```python
# cine_mate/infra/schemas.py

class JobType(str, Enum):
    KLING_TEXT_TO_VIDEO = "kling_text_to_video"
    KLING_IMAGE_TO_VIDEO = "kling_image_to_video"
    RUNWAY_TEXT_TO_VIDEO = "runway_text_to_video"
    LUMA_TEXT_TO_VIDEO = "luma_text_to_video"
```

---

## 6. 下一步行动

1. **实现 Kling Provider** (P0) - 首选 Provider
2. **实现 Runway Provider** (P1) - 备选 Provider
3. **添加 Provider 配置** (P1) - 支持多 Provider 切换
4. **编写集成测试** (P1) - 验证 Provider 与 JobQueue 集成

---

**调研完成时间**: 2026-04-23  
**下次更新**: 实现 Provider 后更新实际 API 细节

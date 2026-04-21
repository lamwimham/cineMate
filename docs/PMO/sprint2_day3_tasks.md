# Sprint 2 Day 3 任务通知

> **To**: 全员
> **From**: PM (AI Assistant)
> **Date**: 2026-04-24 (Sprint 2 Day 3)
> **Priority**: P0-P1

---

## 📋 Day 3 目标

**核心目标**: 实现 Provider 适配器，完成 Video/Image 生成集成

---

## 🎯 任务分配

### hermes (Agent/Gateway 负责人) - P0

| 任务 | 预估 | 优先级 | 验收标准 |
|------|------|--------|----------|
| 实现 Kling Provider | 3h | P0 | `KlingProvider` 类，支持 text-to-video + image-to-video |
| 实现 Runway Provider | 2h | P1 | `RunwayProvider` 类，支持 text-to-video |
| Provider 与 JobQueue 集成 | 1h | P0 | `JobType` 扩展，Worker 调用 Provider |

**交付物**: `cine_mate/adapters/kling_provider.py`, `cine_mate/adapters/runway_provider.py`

---

### copaw (Infra/Skill 负责人) - P0-P1

| 任务 | 预估 | 优先级 | 验收标准 |
|------|------|--------|----------|
| Provider ADR 文档 | 1h | P0 | `docs/adr/ADR-003_provider_adapter.md` |
| BaseVideoProvider 基类 | 1h | P0 | `cine_mate/adapters/base.py` 抽象类 |
| Provider 工厂函数 | 0.5h | P1 | `cine_mate/adapters/factory.py` |
| 与 hermes 协作验证 | 0.5h | P1 | 验证 Kling/Runway Provider 接口 |

**交付物**: `ADR-003`, `base.py`, `factory.py`

---

### claude (QA/Testing 负责人) - P1

| 任务 | 预估 | 优先级 | 验收标准 |
|------|------|--------|----------|
| Provider 单元测试 | 2h | P1 | `tests/unit/adapters/test_kling_provider.py` |
| Provider 集成测试 | 1h | P1 | `tests/integration/test_provider_integration.py` |
| Mock Provider 测试 | 1h | P1 | 无 API Key 可测试 |

**交付物**: Provider 测试文件，覆盖率 >90%

---

## 📅 Day 3 时间安排

| 时间 | 任务 | Owner |
|------|------|-------|
| 09:00 | 任务下发 + Standup | PM |
| 09:30 | BaseVideoProvider 基类实现 | copaw |
| 09:30 | Kling Provider 实现 | hermes |
| 10:30 | Provider ADR 文档 | copaw |
| 11:00 | Provider 与 JobQueue 集成 | hermes |
| 14:00 | Runway Provider 实现 | hermes |
| 14:00 | Provider 单元测试 | claude |
| 15:00 | Provider 工厂函数 | copaw |
| 16:00 | 验证协作会议 | hermes + copaw |
| 17:00 | Daily Standup | 全员 |

---

## 📁 文件结构规划

```
cine_mate/
├── adapters/                   # Provider 适配器 (新增)
│   ├── __init__.py
│   ├── base.py                 # BaseVideoProvider 抽象类 (copaw)
│   ├── factory.py              # Provider 工厂函数 (copaw)
│   ├── kling_provider.py       # Kling API 适配 (hermes)
│   └── runway_provider.py      # Runway API 适配 (hermes)

tests/
├── unit/
│   └── adapters/
│       ├── test_base.py        # 基类测试 (claude)
│       ├── test_kling_provider.py  # Kling 测试 (claude)
│       └── test_runway_provider.py # Runway 测试 (claude)
└── integration/
    └── test_provider_integration.py  # Provider 集成测试 (claude)

docs/
└── adr/
    └── ADR-003_provider_adapter.md   # Provider ADR (copaw)
```

---

## ✅ 验收标准

### hermes 验收

- [ ] KlingProvider 类实现 (text-to-video + image-to-video)
- [ ] RunwayProvider 类实现 (text-to-video)
- [ ] JobType 扩展 (KLING_TEXT_TO_VIDEO, etc.)
- [ ] Worker 调用 Provider 验证
- [ ] Mock Provider 模式支持

### copaw 验收

- [ ] ADR-003 文档完整 (设计决策 + 接口定义)
- [ ] BaseVideoProvider 抽象类 (generate_video + estimate_cost)
- [ ] Provider 工厂函数 (get_provider)
- [ ] 与 hermes 协作验证通过

### claude 验收

- [ ] Provider 单元测试通过
- [ ] Mock Provider 测试通过
- [ ] Provider 集成测试通过
- [ ] 测试覆盖率 >90%

---

## 🔧 技术参考

### BaseVideoProvider 基类设计 (copaw 参考)

```python
# cine_mate/adapters/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class VideoGenerationResult:
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    cost: float
    duration: int
    created_at: datetime

class BaseVideoProvider(ABC):
    """Base class for all video generation providers"""
    
    provider_name: str
    
    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        duration: int = 10,
        resolution: str = "720p",
        image_url: Optional[str] = None,
        **kwargs
    ) -> VideoGenerationResult:
        """Generate video from text or image"""
        pass
    
    @abstractmethod
    def estimate_cost(self, duration: int, resolution: str = "720p") -> float:
        """Estimate cost for video generation"""
        pass
    
    @abstractmethod
    async def check_status(self, job_id: str) -> str:
        """Check job status"""
        pass
    
    @abstractmethod
    async def get_result(self, job_id: str) -> Optional[VideoGenerationResult]:
        """Get final result"""
        pass
```

### KlingProvider 实现 (hermes 参考)

```python
# cine_mate/adapters/kling_provider.py

import aiohttp
from datetime import datetime
from .base import BaseVideoProvider, VideoGenerationResult

class KlingProvider(BaseVideoProvider):
    """Kling AI Video Generation Provider"""
    
    provider_name = "kling"
    
    def __init__(self, api_key: str, base_url: str = "https://api.wavespeed.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = "kling-2.0"
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 10,
        resolution: str = "720p",
        image_url: Optional[str] = None,
        **kwargs
    ) -> VideoGenerationResult:
        mode = "image_to_video" if image_url else "text_to_video"
        
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                f"{self.base_url}/video/generation",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "duration": duration,
                    "resolution": resolution,
                    "mode": mode,
                    "image_url": image_url,
                }
            )
            data = await response.json()
            
            return VideoGenerationResult(
                job_id=data["job_id"],
                status=data["status"],
                video_url=None,
                thumbnail_url=None,
                cost=self.estimate_cost(duration, resolution),
                duration=duration,
                created_at=datetime.now(),
            )
    
    def estimate_cost(self, duration: int, resolution: str = "720p") -> float:
        # $0.075/s for Kling 2.x
        return duration * 0.075
    
    async def check_status(self, job_id: str) -> str:
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"{self.base_url}/video/status/{job_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            data = await response.json()
            return data["status"]
    
    async def get_result(self, job_id: str) -> Optional[VideoGenerationResult]:
        status = await self.check_status(job_id)
        if status != "completed":
            return None
        
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"{self.base_url}/video/result/{job_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            data = await response.json()
            
            return VideoGenerationResult(
                job_id=job_id,
                status="completed",
                video_url=data["video_url"],
                thumbnail_url=data.get("thumbnail_url"),
                cost=self.estimate_cost(data.get("duration", 10)),
                duration=data.get("duration", 10),
                created_at=datetime.now(),
            )
```

---

## 📞 Daily Standup 模板

请各成员回复确认：

```markdown
**Name**: hermes / copaw / claude
**Date**: 2026-04-24 (Day 3)
**Yesterday**: Sprint 2 Day 2 任务完成
**Today**: [Day 3 任务]
**Blockers**: [如有阻塞请填写]
```

---

**签名**: PM (AI Assistant)
**日期**: 2026-04-24
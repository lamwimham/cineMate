# hermes Sprint 2 Day 3 任务

> **To**: hermes (Agent/Gateway 负责人)
> **From**: PM (AI Assistant)
> **Date**: 2026-04-24 (Sprint 2 Day 3)
> **Priority**: P0-P1

---

## 📋 任务清单

| # | 任务 | 预估 | 优先级 | 验收标准 |
|---|------|------|--------|----------|
| 1 | 实现 Kling Provider | 3h | **P0** | `KlingProvider` 类，支持 text-to-video + image-to-video |
| 2 | Provider 与 JobQueue 集成 | 1h | **P0** | `JobType` 扩展，Worker 调用 Provider |
| 3 | 实现 Runway Provider | 2h | P1 | `RunwayProvider` 类，支持 text-to-video |
| 4 | Mock Provider 模式 | 0.5h | P1 | 无 API Key 可测试 |

---

## 🎯 任务详情

### 任务 1: Kling Provider (P0, 3h)

**交付物**: `cine_mate/adapters/kling_provider.py`

**要求**:
- 实现 `BaseVideoProvider` 子类
- 支持 text-to-video (`mode="text_to_video"`)
- 支持 image-to-video (`mode="image_to_video"`, 参数 `image_url`)
- API Key 从环境变量 `KLING_API_KEY` 获取
- 成本估算: `$0.075/s` (Kling 2.x)
- 异步调用 (aiohttp)

**参考**: `docs/research/video_provider_api_survey.md` Kling API 章节

---

### 任务 2: Provider 与 JobQueue 集成 (P0, 1h)

**交付物**: `cine_mate/infra/queue.py` 扩展

**要求**:
- 扩展 `JobType` 枚举:
  ```python
  class JobType(str, Enum):
      KLING_TEXT_TO_VIDEO = "kling_text_to_video"
      KLING_IMAGE_TO_VIDEO = "kling_image_to_video"
      RUNWAY_TEXT_TO_VIDEO = "runway_text_to_video"
  ```
- Worker `execute_job()` 调用对应 Provider
- Job payload 包含 `prompt`, `duration`, `resolution`, `image_url`

---

### 任务 3: Runway Provider (P1, 2h)

**交付物**: `cine_mate/adapters/runway_provider.py`

**要求**:
- 实现 `BaseVideoProvider` 子类
- 支持 text-to-video
- API Key 从环境变量 `RUNWAY_API_KEY` 获取
- 成本估算: `$0.05/s` (Runway Gen-4)
- 异步调用

---

### 任务 4: Mock Provider 模式 (P1, 0.5h)

**要求**:
- `MockVideoProvider` 类 (类似 `MockChatModel`)
- 无 API Key 时自动使用 Mock
- 返回预设视频 URL

---

## 📅 时间安排

| 时间 | 任务 | 预估 |
|------|------|------|
| 09:30 | Kling Provider 实现 | 3h |
| 11:00 | Provider 与 JobQueue 集成 | 1h |
| 14:00 | Runway Provider 实现 | 2h |
| 16:00 | 验证协作会议 (copaw) | 0.5h |
| 17:00 | Daily Standup | - |

---

## 🔧 技术参考

### Provider 基类 (copaw 实现)

```python
# cine_mate/adapters/base.py

class BaseVideoProvider(ABC):
    @abstractmethod
    async def generate_video(prompt, duration, resolution, image_url) -> VideoGenerationResult
    @abstractmethod
    def estimate_cost(duration, resolution) -> float
    @abstractmethod
    async def check_status(job_id) -> str
    @abstractmethod
    async def get_result(job_id) -> VideoGenerationResult
```

### Kling API 调用 (调研报告参考)

```python
# POST https://api.wavespeed.ai/v1/video/generation
{
    "model": "kling-2.0",
    "prompt": "A cyberpunk city at night",
    "duration": 10,
    "resolution": "720p",
    "mode": "text_to_video"  # or "image_to_video"
}

# Response
{
    "job_id": "xxx",
    "status": "pending"
}

# GET https://api.wavespeed.ai/v1/video/status/{job_id}
{
    "status": "completed",
    "video_url": "https://..."
}
```

---

## ✅ 验收清单

- [ ] KlingProvider 类实现
- [ ] text-to-video 支持
- [ ] image-to-video 支持 (image_url 参数)
- [ ] JobType 扩展完成
- [ ] Worker 调用 Provider
- [ ] RunwayProvider 类实现
- [ ] Mock Provider 模式
- [ ] 代码通过 lint 检查

---

## 📞 确认

请回复确认任务开始：

```markdown
**Name**: hermes
**Date**: 2026-04-24 (Day 3)
**Yesterday**: Sprint 2 Day 2 完成 (配置系统 + 真实 Agent)
**Today**: Kling Provider + JobQueue 集成 + Runway Provider
**Blockers**: [如有阻塞请填写]
```

---

**签名**: PM (AI Assistant)
**日期**: 2026-04-24
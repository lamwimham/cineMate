# copaw Sprint 2 Day 3 任务

> **To**: copaw (Infra/Skill 负责人)
> **From**: PM (AI Assistant)
> **Date**: 2026-04-24 (Sprint 2 Day 3)
> **Priority**: P0-P1

---

## 📋 任务清单

| # | 任务 | 预估 | 优先级 | 验收标准 |
|---|------|------|--------|----------|
| 1 | Provider ADR 文档 | 1h | **P0** | `ADR-003_provider_adapter.md` |
| 2 | BaseVideoProvider 基类 | 1h | **P0** | `cine_mate/adapters/base.py` 抽象类 |
| 3 | Provider 工厂函数 | 0.5h | P1 | `cine_mate/adapters/factory.py` |
| 4 | 与 hermes 协作验证 | 0.5h | P1 | 验证 Kling/Runway Provider 接口 |

---

## 🎯 任务详情

### 任务 1: Provider ADR 文档 (P0, 1h)

**交付物**: `docs/adr/ADR-003_provider_adapter.md`

**要求**:
- 设计决策说明 (为什么选择 Adapter Pattern)
- BaseVideoProvider 接口定义
- Provider 与 JobQueue/Worker 集成方案
- 成本估算策略
- Mock Provider 模式说明

**参考 ADR 格式**:
```markdown
# ADR-003: Provider Adapter Pattern

## Status
Accepted

## Context
需要支持多个视频生成 Provider (Kling, Runway, Luma)
...

## Decision
采用 Adapter Pattern + Factory Pattern
...

## Consequences
- 优点: 解耦 Provider 实现
- 缺点: 需维护多个适配器
```

---

### 任务 2: BaseVideoProvider 基类 (P0, 1h)

**交付物**: `cine_mate/adapters/base.py`

**要求**:
- `VideoGenerationResult` dataclass:
  ```python
  @dataclass
  class VideoGenerationResult:
      job_id: str
      status: str  # pending, processing, completed, failed
      video_url: Optional[str]
      thumbnail_url: Optional[str]
      cost: float
      duration: int
      created_at: datetime
  ```
- `BaseVideoProvider` 抽象基类:
  ```python
  class BaseVideoProvider(ABC):
      provider_name: str
      
      @abstractmethod
      async def generate_video(prompt, duration, resolution, image_url) -> VideoGenerationResult
      
      @abstractmethod
      def estimate_cost(duration, resolution) -> float
      
      @abstractmethod
      async def check_status(job_id) -> str
      
      @abstractmethod
      async def get_result(job_id) -> Optional[VideoGenerationResult]
  ```

---

### 任务 3: Provider 工厂函数 (P1, 0.5h)

**交付物**: `cine_mate/adapters/factory.py`

**要求**:
- `get_provider(provider_name, config) -> BaseVideoProvider`
- 支持 "kling", "runway", "mock"
- 从 config 获取 API Key
- 错误处理 (Provider 不存在)

```python
def get_provider(provider_name: str, config: CineMateConfig) -> BaseVideoProvider:
    if provider_name == "kling":
        api_key = os.getenv("KLING_API_KEY")
        if not api_key:
            return MockVideoProvider()
        return KlingProvider(api_key)
    elif provider_name == "runway":
        ...
```

---

### 任务 4: 与 hermes 协作验证 (P1, 0.5h)

**要求**:
- 验证 hermes 实现的 KlingProvider 接口符合 BaseVideoProvider
- 验证 RunwayProvider 接口
- 确保 JobQueue 集成正确

---

## 📅 时间安排

| 时间 | 任务 | 预估 |
|------|------|------|
| 09:30 | BaseVideoProvider 基类实现 | 1h |
| 10:30 | Provider ADR 文档 | 1h |
| 15:00 | Provider 工厂函数 | 0.5h |
| 16:00 | 验证协作会议 (hermes) | 0.5h |
| 17:00 | Daily Standup | - |

---

## 📁 文件结构

```
cine_mate/adapters/
├── __init__.py        # 导出 BaseVideoProvider, get_provider
├── base.py            # BaseVideoProvider + VideoGenerationResult (你负责)
├── factory.py         # get_provider 工厂函数 (你负责)
├── kling_provider.py  # hermes 负责
└── runway_provider.py # hermes 负责

docs/adr/
└── ADR-003_provider_adapter.md  # 你负责
```

---

## ✅ 验收清单

- [ ] ADR-003 文档完整
- [ ] VideoGenerationResult dataclass
- [ ] BaseVideoProvider 抽象基类
- [ ] generate_video() 抽象方法
- [ ] estimate_cost() 抽象方法
- [ ] check_status() 抽象方法
- [ ] get_result() 抽象方法
- [ ] get_provider() 工厂函数
- [ ] Mock Provider 支持
- [ ] 与 hermes 协作验证通过

---

## 📞 确认

请回复确认任务开始：

```markdown
**Name**: copaw
**Date**: 2026-04-24 (Day 3)
**Yesterday**: Sprint 2 Day 2 完成 (Provider 调研 + Infra 验证 + 架构审查)
**Today**: ADR-003 + BaseVideoProvider + factory
**Blockers**: [如有阻塞请填写]
```

---

**签名**: PM (AI Assistant)
**日期**: 2026-04-24
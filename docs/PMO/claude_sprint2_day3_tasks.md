# claude Sprint 2 Day 3 任务

> **To**: claude (QA/Testing 负责人)
> **From**: PM (AI Assistant)
> **Date**: 2026-04-24 (Sprint 2 Day 3)
> **Priority**: P1

---

## 📋 任务清单

| # | 任务 | 预估 | 优先级 | 验收标准 |
|---|------|------|--------|----------|
| 1 | Provider 单元测试 | 2h | **P1** | `tests/unit/adapters/test_kling_provider.py` |
| 2 | Mock Provider 测试 | 1h | **P1** | 无 API Key 可测试 |
| 3 | Provider 集成测试 | 1h | **P1** | `tests/integration/test_provider_integration.py` |

---

## 🎯 任务详情

### 任务 1: Provider 单元测试 (P1, 2h)

**交付物**: 
- `tests/unit/adapters/__init__.py`
- `tests/unit/adapters/test_base.py`
- `tests/unit/adapters/test_kling_provider.py`
- `tests/unit/adapters/test_runway_provider.py`

**要求**:

#### test_base.py (BaseVideoProvider 测试)

```python
class TestVideoGenerationResult:
    def test_create_result()
    def test_result_serialization()
    def test_optional_fields()

class TestBaseVideoProvider:
    def test_abstract_methods()
    def test_provider_name_attribute()
    def test_estimate_cost_interface()
```

#### test_kling_provider.py

```python
class TestKlingProvider:
    def test_provider_name()
    def test_estimate_cost()  # $0.075/s
    def test_generate_video_text_to_video()
    def test_generate_video_image_to_video()
    def test_check_status()
    def test_get_result()
    def test_api_key_from_env()
    def test_mock_mode_without_api_key()
```

#### test_runway_provider.py

```python
class TestRunwayProvider:
    def test_provider_name()
    def test_estimate_cost()  # $0.05/s
    def test_generate_video_text_to_video()
    def test_check_status()
    def test_get_result()
```

---

### 任务 2: Mock Provider 测试 (P1, 1h)

**要求**:
- `MockVideoProvider` 类 (类似 `MockChatModel`)
- 返回预设视频 URL
- 无需 API Key
- 测试覆盖 Mock 模式

```python
class MockVideoProvider(BaseVideoProvider):
    provider_name = "mock"
    
    async def generate_video(...):
        return VideoGenerationResult(
            job_id="mock-job-123",
            status="completed",
            video_url="https://mock.video.url",
            cost=0.0,
            duration=duration,
        )
```

---

### 任务 3: Provider 集成测试 (P1, 1h)

**交付物**: `tests/integration/test_provider_integration.py`

**要求**:
- Provider 与 JobQueue 集成测试
- Worker 执行 Provider 任务
- Mock 模式全链路测试

```python
class TestProviderIntegration:
    async def test_kling_provider_job_queue()
    async def test_worker_execute_kling_job()
    async def test_mock_provider_full_pipeline()
    async def test_provider_factory()
```

---

## 📅 时间安排

| 时间 | 任务 | 预估 |
|------|------|------|
| 14:00 | Provider 单元测试 | 2h |
| 15:00 | Mock Provider 测试 | 1h |
| 16:00 | Provider 集成测试 | 1h |
| 17:00 | Daily Standup | - |

---

## 📁 文件结构

```
tests/
├── unit/
│   └── adapters/
│       ├── __init__.py
│       ├── test_base.py
│       ├── test_kling_provider.py
│       └── test_runway_provider.py
└── integration/
    └── test_provider_integration.py
```

---

## ✅ 验收清单

- [ ] test_base.py 测试通过
- [ ] test_kling_provider.py 测试通过
- [ ] test_runway_provider.py 测试通过
- [ ] MockVideoProvider 类实现
- [ ] Mock Provider 测试通过
- [ ] Provider 集成测试通过
- [ ] 测试覆盖率 >90%
- [ ] CI Checks passing

---

## 📞 确认

请回复确认任务开始：

```markdown
**Name**: claude
**Date**: 2026-04-24 (Day 3)
**Yesterday**: Sprint 2 Day 2 完成 (测试覆盖 +1423 lines)
**Today**: Provider 单元测试 + Mock 测试 + 集成测试
**Blockers**: [如有阻塞请填写]
```

---

**签名**: PM (AI Assistant)
**日期**: 2026-04-24
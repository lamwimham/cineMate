# ADR-003: Video Provider Adapter Architecture

> **Date**: 2026-04-24  
> **Status**: Proposed  
> **Sprint**: 2 Day 3  
> **Owner**: copaw (Infra & Skill 负责人)  
> **Contributors**: hermes, claude

---

## Context

CineMate needs to integrate with multiple upstream video generation providers:
- Kling (ByteDance) - Primary provider
- Runway (Runway ML) - Backup provider
- Luma (Luma AI) - Optional provider

Each provider has:
- Different API endpoints
- Different authentication mechanisms
- Different pricing models
- Different capabilities (text-to-video, image-to-video, etc.)

We need a unified interface to:
1. Abstract away provider-specific details
2. Enable easy provider switching
3. Support fallback/retry logic
4. Track costs and usage per provider

---

## Decision

### Architecture: Provider Adapter Pattern

We will implement a **Provider Adapter Pattern** with:

1. **Abstract Base Class** (`BaseVideoProvider`)
   - Defines common interface for all providers
   - Provides shared validation and retry logic
   - Enforces consistent error handling

2. **Concrete Providers** (`KlingProvider`, `RunwayProvider`, `LumaProvider`)
   - Implement provider-specific API calls
   - Handle provider-specific authentication
   - Translate provider responses to common format

3. **Provider Factory** (`get_provider()`)
   - Creates provider instances from configuration
   - Manages provider lifecycle
   - Supports provider discovery

4. **Provider Registry**
   - Tracks available providers
   - Stores provider capabilities
   - Enables runtime provider selection

### Class Hierarchy

```
BaseVideoProvider (ABC)
├── KlingProvider
├── RunwayProvider
└── LumaProvider
```

### Interface Definition

```python
class BaseVideoProvider(ABC):
    @abstractmethod
    async def generate_video(params: GenerationParams) -> VideoGenerationResult:
        pass
    
    @abstractmethod
    async def get_job_status(job_id: str) -> str:
        pass
    
    @abstractmethod
    async def cancel_job(job_id: str) -> bool:
        pass
    
    @abstractmethod
    def estimate_cost(duration: int, resolution: str, mode: str) -> float:
        pass
```

### Configuration

Provider configuration via YAML:

```yaml
providers:
  kling:
    enabled: true
    api_key: ${KLING_API_KEY}
    base_url: https://api.wavespeed.ai/v1
    priority: 1  # Primary provider
    max_retries: 3
    timeout_seconds: 300
  
  runway:
    enabled: true
    api_key: ${RUNWAY_API_KEY}
    base_url: https://api.runwayml.com/v1
    priority: 2  # Backup provider
    max_retries: 2
    timeout_seconds: 180
  
  luma:
    enabled: false  # Disabled by default
    api_key: ${LUMA_API_KEY}
    base_url: https://api.piapi.ai/v1
    priority: 3
```

---

## Consequences

### Positive

1. **Abstraction**: Engine code doesn't need to know about specific providers
2. **Extensibility**: Easy to add new providers (implement base class)
3. **Testability**: Can mock providers for testing
4. **Flexibility**: Can switch providers via configuration
5. **Fallback**: Can implement automatic provider failover
6. **Cost Tracking**: Unified cost estimation across providers

### Negative

1. **Complexity**: Additional abstraction layer
2. **Learning Curve**: Team needs to understand the pattern
3. **Overhead**: Slight performance overhead from abstraction
4. **Maintenance**: Need to update all providers when base class changes

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Provider API changes | Medium | Abstract common operations, isolate provider-specific code |
| Provider downtime | High | Implement fallback logic, health checks |
| Cost overruns | Medium | Add cost limits, usage tracking |
| API key management | High | Use environment variables, secret management |

---

## Implementation Plan

### Phase 1: Foundation (Sprint 2 Day 3)

- [x] `BaseVideoProvider` abstract base class
- [ ] `GenerationParams` dataclass
- [ ] `VideoGenerationResult` dataclass
- [ ] Provider exceptions (`ProviderError`, etc.)

### Phase 2: Provider Implementations (Sprint 2 Day 3-4)

- [ ] `KlingProvider` (P0)
- [ ] `RunwayProvider` (P1)
- [ ] `LumaProvider` (P2, optional)

### Phase 3: Factory & Registry (Sprint 2 Day 3)

- [ ] `ProviderFactory` class
- [ ] Provider registry
- [ ] Configuration loading

### Phase 4: Integration (Sprint 2 Day 4)

- [ ] JobQueue integration
- [ ] Worker integration
- [ ] End-to-end testing

### Phase 5: Testing (Sprint 2 Day 3-4)

- [ ] Unit tests for each provider
- [ ] Integration tests
- [ ] Mock provider for testing

---

## Alternatives Considered

### Alternative 1: Direct Integration

**Approach**: Call provider APIs directly from Engine/Worker

**Pros**:
- Simpler, no abstraction
- Less code

**Cons**:
- Tight coupling to specific providers
- Hard to switch providers
- Code duplication for each provider

**Decision**: ❌ Rejected - Not scalable

---

### Alternative 2: Strategy Pattern

**Approach**: Use Strategy pattern with dependency injection

**Pros**:
- More flexible than Adapter
- Better for runtime switching

**Cons**:
- More complex
- Overkill for current needs

**Decision**: ❌ Rejected - Adapter pattern is sufficient

---

### Alternative 3: Plugin Architecture

**Approach**: Providers as loadable plugins

**Pros**:
- Maximum extensibility
- Third-party providers possible

**Cons**:
- Overly complex for MVP
- Security concerns with dynamic loading

**Decision**: ❌ Rejected - Can evolve to this later if needed

---

## Provider Comparison

| Provider | Price (10s) | Quality | API Maturity | Recommendation |
|----------|-------------|---------|--------------|----------------|
| Kling 2.x | $0.75 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Primary |
| Runway Gen-4 | $0.50 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Backup |
| Luma Dream | $1.00 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⚠️ Optional |

---

## Testing Strategy

### Unit Tests

```python
class TestKlingProvider:
    async def test_generate_video_success(self):
        provider = KlingProvider(api_key="test_key")
        result = await provider.generate_video(
            GenerationParams(prompt="test")
        )
        assert result.status == "completed"
    
    async def test_estimate_cost(self):
        provider = KlingProvider(api_key="test_key")
        cost = provider.estimate_cost(duration_seconds=10)
        assert cost == 0.75
```

### Integration Tests

```python
class TestProviderIntegration:
    async def test_kling_real_api(self):
        # Only run with real API key
        provider = KlingProvider(api_key=os.environ["KLING_API_KEY"])
        result = await provider.generate_video(...)
        assert result.video_url is not None
```

### Mock Provider

```python
class MockVideoProvider(BaseVideoProvider):
    """Mock provider for testing without API calls"""
    
    async def generate_video(self, params: GenerationParams):
        return VideoGenerationResult(
            job_id="mock_job_123",
            status="completed",
            video_url="https://mock.example.com/video.mp4",
            cost=0.0
        )
```

---

## Metrics & Monitoring

### Key Metrics

1. **Success Rate**: % of successful generations per provider
2. **Latency**: Time from request to completion
3. **Cost**: Total cost per provider per day
4. **Error Rate**: % of failed requests by error type
5. **Usage**: Number of generations per provider

### Alerting

- Provider error rate > 10% → Alert
- Provider latency > 5min → Alert
- Daily cost > budget → Alert

---

## Future Considerations

### Sprint 3+

1. **Provider Failover**: Automatic switch to backup provider on failure
2. **Load Balancing**: Distribute load across multiple providers
3. **Cost Optimization**: Automatically choose cheapest provider
4. **Quality Scoring**: Track and compare output quality
5. **A/B Testing**: Test multiple providers for same prompt

### Sprint 4+

1. **Multi-Provider**: Generate same video with multiple providers
2. **Provider Selection AI**: ML-based provider selection
3. **Custom Providers**: Support customer-provided providers

---

## References

- [Provider API Survey](../research/video_provider_api_survey.md)
- [Architecture Review](../review/architecture_review_2026-04-23.md)
- [BaseVideoProvider Implementation](../../cine_mate/adapters/base.py)

---

**Approved by**: [Pending]  
**Implementation**: Sprint 2 Day 3-4  
**Review Date**: 2026-04-30

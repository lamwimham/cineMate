# 🚨 P0 Critical Fixes Required

> **Labels**: `P0`, `critical`, `bug`
> **Sprint**: 1, Day 4
> **Reporter**: claude (Code Review)
> **Assignee**: hermes
> **Due**: End of Day 4 (2026-04-24)

---

## Issue 1: Mock Mode Not Testable

**Severity**: 🔴 P0 - Blocks Testing  
**File**: `cine_mate/agents/director_agent.py`  
**Lines**: 67-79

### Problem
DirectorAgent cannot be tested in mock mode. The agent requires real API calls to initialize, making unit tests impossible without valid API keys.

### Current Code (Issue)
```python
# director_agent.py L67-79
class DirectorAgent(ReActAgent):
    def __init__(self, ...):
        # Always initializes real model
        self.model = DashScopeChatModel(...)  # Requires real API key
        # No mock/test mode support
```

### Expected Behavior
```python
class DirectorAgent(ReActAgent):
    def __init__(self, ..., use_mock: bool = False):
        if use_mock:
            self.model = MockModel()  # Test-friendly mock
        else:
            self.model = DashScopeChatModel(...)
```

### Fix Required
- [ ] Add `use_mock` parameter to `__init__`
- [ ] Implement `MockModel` class for testing
- [ ] Update tests to use mock mode

---

## Issue 2: API Misuse - find_stuck_executions

**Severity**: 🔴 P0 - Runtime Error  
**File**: `cine_mate/agents/tools/engine_tools.py`  
**Line**: 85

### Problem
Incorrect API usage of `find_stuck_executions` method. The method signature or usage pattern is wrong, causing runtime errors.

### Current Code (Issue)
```python
# engine_tools.py L85
stuck = await store.find_stuck_executions(timeout=300)
# Error: find_stuck_executions doesn't exist or wrong params
```

### Expected Behavior
Check `cine_mate/core/store.py` for correct API:
```python
# Check actual Store implementation
stuck = await store.find_stuck_executions(
    run_id=run_id,
    timeout_seconds=300
)
```

### Fix Required
- [ ] Verify correct method name in `store.py`
- [ ] Verify correct parameter names
- [ ] Update call site with correct API
- [ ] Add error handling

---

## Acceptance Criteria

- [ ] Both issues fixed and tested
- [ ] `pytest tests/unit/agents/` passes
- [ ] Code Review approved by claude
- [ ] PR merged to main before Day 4 end

---

## Related

- Original Code Review: docs/code_review_sprint1_day3.md
- Sprint 1 Plan: docs/PMO/sprint_1_team.md

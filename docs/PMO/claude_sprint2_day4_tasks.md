# claude Sprint 2 Day 4 Tasks

> **Owner**: claude (QA & Testing 负责人)
> **Sprint**: 2 Day 4 (2026-04-25)
> **通知日期**: 2026-04-24

---

## 📋 任务列表

| # | 任务 | 优先级 | 预估工时 | 交付物 |
|---|------|--------|----------|--------|
| 1 | 环境验证 + pytest 运行 | 🔴 P0 | 0.5h | pytest 可运行验证 |
| 2 | 运行完整测试验证 | 🟡 P1 | 1h | pytest 全通过报告 |
| 3 | 测试覆盖率报告 | 🟡 P1 | 0.5h | docs/testing/sprint2_coverage_report.md |
| 4 | Provider 测试验证 | 🟡 P1 | 0.5h | Provider tests 验证报告 |

**总工时**: 2.5h

---

## 🔴 P0: 环境验证 + pytest 运行

### 环境问题描述

```
which python → /Users/lianwenhua/indie/hermes-agent/venv/bin/python
which pip    → /Users/lianwenhua/Library/Python/3.9/bin/pip
```

pytest 运行在 hermes-agent venv，但 networkx 安装在用户级 Python 3.9。

### 环境验证步骤

```bash
# 等待 hermes + copaw 修复环境后验证

# 1. 验证 pytest 可运行
pytest --version

# 2. 验证 networkx 可导入
python -c "import networkx; print(networkx.__version__)"

# 3. 运行 Provider 单元测试
pytest tests/unit/adapters/ -v

# 4. 运行 Provider 集成测试
pytest tests/integration/test_provider_integration.py -v
```

### 验收标准

- `pytest tests/unit/adapters/` 全通过
- `pytest tests/integration/test_provider_integration.py` 全通过

---

## 🟡 P1: 运行完整测试验证

### 测试范围

| 测试类别 | 文件 | 预期结果 |
|----------|------|----------|
| Provider 单元测试 | tests/unit/adapters/test_provider_base.py | ✅ 全通过 |
| Provider 集成测试 | tests/integration/test_provider_integration.py | ✅ 全通过 |
| Engine 测试 | tests/unit/engine/ | ✅ 全通过 |
| Queue 集成测试 | tests/integration/test_queue_integration.py | ✅ 全通过 |
| Orchestrator 测试 | tests/test_orchestrator.py | ✅ 全通过 |

### 运行命令

```bash
# 完整测试
pytest tests/ -v --tb=short

# 分模块测试
pytest tests/unit/ -v
pytest tests/integration/ -v

# 测试统计
pytest tests/ --collect-only | grep "test session starts"
```

### 交付物

- pytest 全通过报告
- 测试统计 (通过数/总数)
- 失败测试分析 (如有)

---

## 🟡 P1: 测试覆盖率报告

### 覆盖率目标

| 模块 | 目标覆盖率 | 当前覆盖率 (待测) |
|------|------------|------------------|
| cine_mate/adapters | >90% | ⏳ |
| cine_mate/infra | >80% | ⏳ |
| cine_mate/engine | >75% | ⏳ |
| cine_mate/agents | >70% | ⏳ |
| **整体** | **>80%** | **⏳** |

### 运行覆盖率

```bash
# 覆盖率测试
pytest tests/ --cov=cine_mate --cov-report=term --cov-report=html

# 查看 HTML 报告
open htmlcov/index.html

# 分模块覆盖率
pytest tests/unit/adapters/ --cov=cine_mate/adapters --cov-report=term
pytest tests/unit/engine/ --cov=cine_mate/engine --cov-report=term
```

### 报告内容

```markdown
# Sprint 2 Coverage Report

## Overall Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| cine_mate/adapters | X% | ✅/⚠️ |
| cine_mate/infra | X% | ✅/⚠️ |
| cine_mate/engine | X% | ✅/⚠️ |
| cine_mate/agents | X% | ✅/⚠️ |

## Provider Adapter Coverage

| File | Lines | Covered | Coverage |
|------|-------|---------|----------|
| base.py | 280 | X | X% |
| factory.py | 157 | X | X% |
| kling_provider.py | 192 | X | X% |
| runway_provider.py | 203 | X | X% |
| mock_provider.py | 107 | X | X% |

## Missing Coverage

| Module | Missing Lines | Priority |
|--------|---------------|----------|
| ... | ... | ... |
```

### 交付物

- `docs/testing/sprint2_coverage_report.md`
- 覆盖率 HTML 报告 (htmlcov/)
- 覆盖率统计表

---

## 🟡 P1: Provider 测试验证

### Provider 测试清单

| 测试类 | 测试方法 | 验收标准 |
|--------|----------|----------|
| TestVideoGenerationResult | test_result_creation | ✅ 通过 |
| TestVideoGenerationResult | test_result_status_checks | ✅ 通过 |
| TestGenerationParams | test_params_defaults | ✅ 通过 |
| TestGenerationParams | test_params_validation | ✅ 通过 |
| TestBaseVideoProvider | test_provider_init | ✅ 通过 |
| TestBaseVideoProvider | test_health_check | ✅ 通过 |
| TestProviderFactory | test_get_provider | ✅ 通过 |
| TestProviderFactory | test_register_provider | ✅ 通过 |
| TestProviderFallback | test_fallback_chain | ✅ 通过 |
| TestGenerationFlow | test_text_to_video | ✅ 通过 |

### 验证命令

```bash
# Provider 单元测试
pytest tests/unit/adapters/test_provider_base.py -v

# Provider 集成测试
pytest tests/integration/test_provider_integration.py -v

# Provider 覆盖率
pytest tests/unit/adapters/ tests/integration/test_provider_integration.py \
  --cov=cine_mate/adapters --cov-report=term
```

### 交付物

- Provider 测试验证报告
- 通过/失败统计
- 覆盖率统计

---

## 📅 时间表

| 时间 | 任务 | 优先级 |
|------|------|--------|
| 10:00 | 环境验证 + pytest 运行 | 🔴 P0 |
| 10:30 | 运行完整测试验证 | 🟡 P1 |
| 13:00 | 测试覆盖率报告 | 🟡 P1 |
| 13:30 | Provider 测试验证 | 🟡 P1 |

---

## 📊 验收标准

| 标准 | 要求 |
|------|------|
| pytest 可运行 | pytest tests/ 全通过 |
| 覆盖率报告 | sprint2_coverage_report.md 完成 |
| Provider 测试验证 | Provider tests 验证报告完成 |

---

**通知发送**: ✅
**签名**: PM (AI Assistant)
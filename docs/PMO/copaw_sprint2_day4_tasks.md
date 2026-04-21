# copaw Sprint 2 Day 4 Tasks

> **Owner**: copaw (Infra & Skill 负责人)
> **Sprint**: 2 Day 4 (2026-04-25)
> **通知日期**: 2026-04-24

---

## 📋 任务列表

| # | 任务 | 优先级 | 预估工时 | 交付物 |
|---|------|--------|----------|--------|
| 1 | 协助修复 Python 环境 | 🔴 P0 | 0.5h | venv 依赖验证 |
| 2 | 整体代码审查 | 🟡 P1 | 2h | docs/PMO/sprint2_code_review.md |
| 3 | 架构健康度报告 | 🟡 P1 | 0.5h | docs/PMO/sprint2_architecture_health.md |

**总工时**: 3h

---

## 🔴 P0: 修复 Python 环境

### 问题描述

```
which python → /Users/lianwenhua/indie/hermes-agent/venv/bin/python
which pip    → /Users/lianwenhua/Library/Python/3.9/bin/pip
```

pytest 运行在 hermes-agent venv，但 networkx 安装在用户级 Python 3.9。

### 解决方案

与 hermes 协作，验证 venv 配置：

```bash
# 验证 pyproject.toml 依赖
cat pyproject.toml | grep -A 20 dependencies

# 安装项目依赖
pip install -e .[dev]

# 验证安装
python -c "import networkx; print(networkx.__version__)"
pytest --version
```

### 验收标准

- `pytest tests/` 可正常运行
- `pytest tests/unit/adapters/` 全通过

---

## 🟡 P1: 整体代码审查

### 审查范围

| 模块 | 文件 | 行数 | Sprint |
|------|------|------|--------|
| Config System | cine_mate/config.py | ~300 | Day 2 |
| EventBus | cine_mate/infra/event_bus.py | ~150 | Day 1 |
| JobQueue | cine_mate/infra/job_queue.py | ~200 | Day 1 |
| Worker | cine_mate/infra/worker.py | ~300 | Day 1-3 |
| **Provider Adapter** | **cine_mate/adapters/** | **~940** | **Day 3** |
| Engine | cine_mate/engine/ | ~400 | Sprint 1 |

### 审查清单

#### Provider Adapter 审查

| 项目 | 检查内容 | 状态 |
|------|----------|------|
| BaseVideoProvider | 抽象方法定义完整 | ⏳ |
| VideoGenerationResult | 数据类定义正确 | ⏳ |
| GenerationParams | 参数验证完整 | ⏳ |
| KlingProvider | API 调用正确 | ⏳ |
| RunwayProvider | API 调用正确 | ⏳ |
| MockProvider | 测试 Mock 完整 | ⏳ |
| Provider Factory | 工厂函数正确 | ⏳ |
| Worker 集成 | Provider 路由正确 | ⏳ |

#### 架构一致性审查

| 项目 | 检查内容 | 状态 |
|------|----------|------|
| 依赖注入 | Agents + Provider 正确注入 | ⏳ |
| 异步处理 | async/await 正确使用 | ⏳ |
| 错误处理 | ProviderError 正确使用 | ⏳ |
| 配置管理 | Provider 配置正确加载 | ⏳ |

### 交付物

- `docs/PMO/sprint2_code_review.md`
- 审查报告包含：
  - Provider Adapter 审查结果
  - 架构一致性审查结果
  - 发现问题列表
  - 改进建议

---

## 🟡 P1: 架构健康度报告

### 报告内容

| 模块 | 状态 | 问题 | 建议 |
|------|------|------|------|
| Config System | ⏳ | 待审查 | 待审查 |
| EventBus | ⏳ | 待审查 | 待审查 |
| JobQueue | ⏳ | 待审查 | 待审查 |
| Worker | ⏳ | 待审查 | 待审查 |
| Provider Adapter | ⏳ | 待审查 | 待审查 |
| Engine (DAG/FSM) | ⏳ | 待审查 | 待审查 |

### 健康度评分

| 模块 | 评分 (1-5) | 问题数 | 建议 |
|------|------------|--------|------|
| Config System | ⏳ | - | - |
| EventBus | ⏳ | - | - |
| JobQueue | ⏳ | - | - |
| Worker | ⏳ | - | - |
| Provider Adapter | ⏳ | - | - |
| Engine | ⏳ | - | - |

### 交付物

- `docs/PMO/sprint2_architecture_health.md`
- 报告包含：
  - 各模块健康度评分
  - 问题汇总
  - Sprint 3 改进建议

---

## 📅 时间表

| 时间 | 任务 | 优先级 |
|------|------|--------|
| 09:00 | 协助修复 Python 环境 | 🔴 P0 |
| 10:00 | 环境验证 | 🔴 P0 |
| 11:00 | 整体代码审查开始 | 🟡 P1 |
| 12:00 | Lunch | - |
| 13:00 | 代码审查继续 | 🟡 P1 |
| 14:00 | 架构健康度报告 | 🟡 P1 |

---

## 📊 验收标准

| 标准 | 要求 |
|------|------|
| Python 环境修复 | pytest 可正常运行 |
| 代码审查报告 | sprint2_code_review.md 完成 |
| 架构健康度报告 | sprint2_architecture_health.md 完成 |

---

**通知发送**: ✅
**签名**: PM (AI Assistant)
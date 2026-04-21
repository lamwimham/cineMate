# claude Sprint 2 Day 1 任务通知

> **To**: claude (QA/Testing 负责人)
> **From**: PM (AI Assistant)
> **Date**: 2026-04-22 (Sprint 2 Day 1)
> **Priority**: P0

---

## 📋 Day 1 任务清单

### 任务 1: CI/CD GitHub Actions 配置 (预计 2h)

**目标**: 配置 GitHub Actions 自动测试流水线

**现状**:
- ❌ CI/CD 未配置
- ✅ 测试已就绪 (21 files, 2007 lines)

---

## 🔧 GitHub Actions 配置

### 文件: `.github/workflows/test.yml`

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run linting
        run: |
          ruff check cine_mate tests

      - name: Run tests with coverage
        run: |
          pytest --cov=cine_mate --cov-report=xml --cov-report=html
        env:
          REDIS_URL: redis://localhost:6379

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
```

---

## ✅ 验收标准

- [ ] `.github/workflows/test.yml` 创建
- [ ] Push 到 main 触发 CI
- [ ] PR 触发 CI
- [ ] Redis service container 运行
- [ ] pytest 通过
- [ ] coverage report 生成
- [ ] Codecov 上传 (可选)

---

## 📝 提交要求

### PR 格式

```
Title: ci: Add GitHub Actions test workflow

Body:
- Add pytest + coverage workflow
- Add Redis service container
- Add ruff linting
- Trigger on push to main and PR

Refs: docs/PMO/sprint1_final_report.md (CI/CD missing)
```

---

## ⏰ 时间安排

| 时间 | 任务 |
|------|------|
| 09:30 - 11:00 | 创建 `.github/workflows/test.yml` |
| 11:00 - 12:00 | 测试 CI 运行 |
| 17:00 | Daily Standup |

---

## 📞 协作

- **Standup**: 17:00 汇报进度

---

**签名**: PM (AI Assistant)
**日期**: 2026-04-22
# hermes Sprint 2 Day 4 Tasks

> **Owner**: hermes (Agent & Gateway 负责人)
> **Sprint**: 2 Day 4 (2026-04-25)
> **通知日期**: 2026-04-24

---

## 📋 任务列表

| # | 任务 | 优先级 | 预估工时 | 交付物 |
|---|------|--------|----------|--------|
| 1 | 协助修复 Python 环境 | 🔴 P0 | 0.5h | venv 依赖安装 |
| 2 | Demo 脚本准备 | 🟢 P2 | 1h | scripts/demo_sprint2.py |
| 3 | Demo 流程文档 | 🟢 P2 | 0.5h | docs/demo/sprint2_demo_guide.md |

**总工时**: 2h

---

## 🔴 P0: 修复 Python 环境

### 问题描述

```
which python → /Users/lianwenhua/indie/hermes-agent/venv/bin/python
which pip    → /Users/lianwenhua/Library/Python/3.9/bin/pip
```

pytest 运行在 hermes-agent venv，但 networkx 安装在用户级 Python 3.9。

### 解决方案

```bash
# 方案 1: 使用项目级 venv
cd /Users/lianwenhua/indie/Agents/qwen/cineMate
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# 方案 2: 在现有 venv 中安装依赖
source /Users/lianwenhua/indie/hermes-agent/venv/bin/activate
pip install networkx pytest pytest-asyncio pytest-cov
```

### 验收标准

- `pytest tests/` 可正常运行
- `pytest tests/unit/adapters/` 全通过

---

## 🟢 P2: Demo 脚本准备

### Demo 内容

```python
# scripts/demo_sprint2.py

"""
Sprint 2 Demo - Provider Adapter + Agent + Worker

演示内容:
1. Provider Factory 创建 Kling Provider
2. text_to_video 生成流程
3. image_to_video 生成流程
4. Worker + Provider 集成
5. Mock Provider 测试流程
"""

def demo_provider_factory():
    """演示 Provider Factory 创建 Provider"""
    from cine_mate.adapters.factory import get_provider, get_primary_provider
    
    # 创建 Kling Provider
    kling = get_provider("kling", api_key="demo_key")
    print(f"✅ Kling Provider: {kling.provider_name}")
    
    # 创建 Runway Provider
    runway = get_provider("runway", api_key="demo_key")
    print(f"✅ Runway Provider: {runway.provider_name}")

def demo_text_to_video():
    """演示 text_to_video 生成流程"""
    from cine_mate.adapters.mock_provider import MockVideoProvider
    from cine_mate.adapters.base import GenerationParams, VideoGenerationMode
    
    provider = MockVideoProvider(api_key="demo")
    params = GenerationParams(
        prompt="A cat playing piano",
        duration_seconds=5,
        mode=VideoGenerationMode.TEXT_TO_VIDEO,
    )
    
    cost = provider.estimate_cost(5, "720p")
    print(f"💰 Cost estimate: ${cost:.2f}")
    
    # 使用 generate_and_wait
    result = provider.generate_and_wait(params)
    print(f"✅ Generated: {result.video_url}")

def demo_worker_integration():
    """演示 Worker + Provider 集成"""
    from cine_mate.infra.worker import Worker
    from cine_mate.infra.schemas import JobType
    
    worker = Worker()
    print(f"✅ Worker initialized")
    
    # 模拟 Kling job
    print(f"📋 Supported JobTypes: KLING_TEXT_TO_VIDEO, KLING_IMAGE_TO_VIDEO")

if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 2 Demo - Provider Adapter + Agent + Worker")
    print("=" * 60)
    
    demo_provider_factory()
    demo_text_to_video()
    demo_worker_integration()
    
    print("\n✅ Demo Complete!")
```

### 交付物

- `scripts/demo_sprint2.py` - Demo 脚本
- 脚本可正常运行
- 输出清晰易懂

---

## 🟢 P2: Demo 流程文档

### 文档内容

```markdown
# Sprint 2 Demo Guide

## Demo 流程

### 1. Provider Factory Demo (1 min)
- 展示 get_provider 创建 Kling + Runway
- 展示 Provider 属性 (name, modes, cost)

### 2. text_to_video Demo (2 min)
- 展示 GenerationParams 创建
- 展示 estimate_cost 计算
- 展示 generate_and_wait 流程

### 3. Worker + Provider Demo (2 min)
- 展示 Worker 初始化
- 展示 JobType 扩展
- 展示 Provider 路由

### 4. Q&A (5 min)
```

### 交付物

- `docs/demo/sprint2_demo_guide.md`
- Demo 流程清晰
- 时间分配合理

---

## 📅 时间表

| 时间 | 任务 | 优先级 |
|------|------|--------|
| 09:00 | 协助修复 Python 环境 | 🔴 P0 |
| 10:00 | 环境验证 | 🔴 P0 |
| 15:00 | Demo 脚本准备 | 🟢 P2 |
| 16:00 | Demo 流程文档 | 🟢 P2 |

---

## 📊 验收标准

| 标准 | 要求 |
|------|------|
| Python 环境修复 | pytest 可正常运行 |
| Demo 脚本 | demo_sprint2.py 可运行 |
| Demo 文档 | sprint2_demo_guide.md 完成 |

---

**通知发送**: ✅
**签名**: PM (AI Assistant)
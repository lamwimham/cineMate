# CineMate Sprint 2 演示指南

> **目标**: 验证 Sprint 2 核心功能 —— Provider 适配器、Agent 集成、Worker 集成、配置系统
> **预计时长**: 5-8 分钟
> **运行环境**: Python 3.11+, Redis, 项目 venv

---

## 1. 环境准备

确保已安装项目依赖并激活虚拟环境：

```bash
cd projects/cinemate
source .venv/bin/activate
```

**无需 API Key**：演示脚本使用 Mock Provider 运行，不依赖外部 API。

---

## 2. 运行演示脚本

完整演示所有功能：

```bash
python scripts/demo_sprint2.py
```

运行指定章节：

```bash
# 仅演示 Provider Factory
python scripts/demo_sprint2.py --section factory

# 仅演示 Worker 集成
python scripts/demo_sprint2.py --section worker

# 演示多个章节
python scripts/demo_sprint2.py --section text_to_video image_to_video mock
```

**可用章节列表**:
| 章节名 | 说明 |
|--------|------|
| `factory` | Provider Factory 创建 Kling + Runway + Mock |
| `text_to_video` | 文本到视频生成流程 |
| `image_to_video` | 图像到视频生成流程 |
| `generate_and_wait` | 自动轮询便捷方法 |
| `worker` | Worker + Provider JobType 路由 |
| `config` | 配置系统多模型 Provider 配置 |
| `mock` | 仅运行所有 Mock 相关章节 |
| `all` | 运行所有章节 (默认) |

---

## 3. 演示内容详解

### 3.1 Provider Factory

验证三种 Provider 是否都继承自 `BaseVideoProvider` 抽象类：

```
  BaseVideoProvider: BaseVideoProvider
    Abstract methods: frozenset({'estimate_cost', 'generate_video', 'get_result', 'check_status'})

  KlingProvider:
    provider_name: kling
    Inherits BaseVideoProvider: True

  RunwayProvider:
    provider_name: runway
    Inherits BaseVideoProvider: True

  MockVideoProvider:
    provider_name: mock
    Inherits BaseVideoProvider: True
    Estimate cost (10s): $0.00
```

**关键验证点**:
- 所有 Provider 实现统一的抽象接口
- Mock Provider 无需 API Key 即可使用
- 成本估算功能正常

### 3.2 text_to_video 生成流程

演示完整的文本到视频生成链路：

1. **Estimate cost**: 预估生成成本
2. **Submit generation**: 提交生成任务，获取 `job_id`
3. **Check status**: 查询任务状态
4. **Get result**: 获取最终视频 URL

```
  Prompt: "A cyberpunk city at night with neon lights and rain"
  Provider: mock

  [Step 1] Estimate cost: $0.00
  [Step 2] Submitting generation job...
    job_id: mock_xxxxxxxx
    status: ProviderStatus.PENDING
  [Step 3] Check status: ProviderStatus.COMPLETED
  [Step 4] Result:
    video_url: https://example.com/mock_video.mp4
    duration:  10s
```

### 3.3 image_to_video 生成流程

演示基于图像的视频生成（自动识别 image_to_video 模式）：

```
  Source image: https://example.com/cyberpunk_city.jpg
  [Step 1] Submitting image_to_video job...
    job_id: mock_xxxxxxxx
    mode: image_to_video
```

**关键验证点**:
- 传入 `image_url` 参数时自动切换到 image_to_video 模式
- 返回结果包含正确的 mode 标识

### 3.4 generate_and_wait 便捷方法

演示 `generate_and_wait()` 方法的自动轮询功能：

```
  Using provider.generate_and_wait()...
  Completed in 2.0s:
    video_url: https://example.com/mock_video.mp4
    status:    ProviderStatus.COMPLETED
    duration:  10s
    cost:      $0.00
```

**关键验证点**:
- 自动提交、轮询、等待完成
- 模拟延迟正常工作

### 3.5 Worker + Provider 集成

展示 Worker 如何根据 `JobType` 路由到对应的 Provider：

```
  Available JobTypes:
    - kling_text_to_video
    - kling_image_to_video
    - runway_text_to_video
    - mock_text_to_video
    - mock_image_to_video

  Worker routing logic:
    kling_text_to_video            → KlingProvider.generate_and_wait()
    kling_image_to_video           → KlingProvider.generate_and_wait(image_url=...)
    runway_text_to_video           → RunwayProvider.generate_and_wait()
    mock_text_to_video             → MockVideoProvider.generate_and_wait()
```

### 3.6 配置系统

展示多模型 Provider 的配置结构：

```
  LLM 配置:
    Primary: dashscope_qwen/qwen-max
    Fallback: dashscope_qwen/qwen-plus

  Video 配置:
    I2V Primary: kling/kling-v1.6-pro
    T2V Primary: runway/runway-gen3-alpha

  Cost Tiers (I2V):
    Primary   : kling/kling-v1.6-pro
    Fallback  : luma/luma-dream-machine
    Budget    : minimax/minimax-video-01
```

---

## 4. 演示时间线

| 步骤 | 内容 | 时长 | 说明 |
|------|------|------|------|
| 1 | Provider Factory | 1 min | 展示 Kling/Runway/Mock 继承关系 |
| 2 | text_to_video | 2 min | 完整生成流程 (估算→提交→查询→结果) |
| 3 | image_to_video | 1 min | 基于图像的自动生成 |
| 4 | Worker + Provider | 2 min | JobType 路由逻辑 |
| 5 | 配置系统 | 1 min | 多模型 Provider 配置展示 |
| 6 | Q&A | 5 min | 预设问题与解答 |
| **总计** | | **~12 min** | |

---

## 5. Q&A 预设问题

### Q1: 为什么需要 Provider 抽象层？
**A**: 不同的视频生成 API (Kling, Runway, Luma 等) 有不同的接口和参数。通过 `BaseVideoProvider` 抽象层，我们统一了调用接口。新增 Provider 只需实现 `generate_video`, `estimate_cost`, `check_status`, `get_result` 四个方法，Worker 路由逻辑无需修改。

### Q2: Mock Provider 的作用是什么？
**A**: 三个作用：
1. **开发测试**: 无需 API Key 即可验证完整流程
2. **CI 集成**: 在 CI/CD 环境中无需配置外部 API
3. **演示准备**: Sprint Review 时不依赖网络和外部服务

### Q3: Worker 是如何路由到对应 Provider 的？
**A**: Worker 根据 `JobType` 枚举值进行路由。例如 `kling_text_to_video` 调用 `KlingProvider`，`runway_text_to_video` 调用 `RunwayProvider`。路由逻辑在 `worker.py` 的 `_execute_by_type()` 函数中实现。

### Q4: 如果 Kling API 调用失败怎么办？
**A**: 当前实现中，Worker 会通过 Redis 发布 `node_failed` 事件，Orchestrator 收到后触发重试或降级逻辑。配置系统中已定义 Fallback Provider (如 Kling → Luma)，可在运行时切换。

### Q5: 配置系统如何管理 API Key？
**A**: API Key 通过环境变量管理 (如 `KLING_API_KEY`, `RUNWAY_API_KEY`)。`defaults.yaml` 中定义了每个 Provider 对应的环境变量名。启动时可通过 `validate_api_keys()` 检查缺失的 Key。

### Q6: 真实 API 调用和 Mock 调用有什么区别？
**A**: 调用流程完全一致。区别在于：
- **Mock**: 立即返回预设结果，零成本，用于测试/演示
- **真实**: 调用外部 API，异步轮询直到完成，产生实际费用

---

## 6. 预期输出摘要

完整运行应输出：

```
╔══════════════════════════════════════════════════════════╗
║        CineMate Sprint 2 Demo                           ║
║  Provider Adapter + Agent + Worker Integration          ║
╚══════════════════════════════════════════════════════════╝

# 1. Provider Factory ...
  ✅ All providers registered successfully.

# 2. text_to_video ...
  ✅ text_to_video flow completed.

# 3. image_to_video ...
  ✅ image_to_video flow completed.

# 4. generate_and_wait ...
  ✅ generate_and_wait completed.

# 5. Worker + Provider ...
  ✅ Worker + Provider integration verified.

# 6. 配置系统 ...
  ✅ Configuration system verified.

╔══════════════════════════════════════════════════════════╗
║        🎉  Sprint 2 Demo Complete!                      ║
╚══════════════════════════════════════════════════════════╝
```

---

## 7. 常见问题

| 问题 | 解决方法 |
|------|----------|
| `ModuleNotFoundError: No module named 'cine_mate'` | 确保已 `source .venv/bin/activate` |
| `Demo failed: KLING_API_KEY not set` | 确保运行的是 Mock Provider 章节，或设置环境变量 |
| Redis 连接失败 | 确保 `redis-server` 正在运行（仅 Worker 集成章节需要） |

---

## 8. 相关文档

- [Provider 适配器 ADR](../adr/ADR-003_provider_adapter.md)
- [Sprint 2 任务文档](../PMO/hermes_sprint2_day3_tasks.md)
- [Issue/PR 格式规范](../standards/issue_pr_title_format.md)

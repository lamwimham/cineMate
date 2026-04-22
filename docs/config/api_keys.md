# CineMate API Key 配置指南

> **Version**: 1.0.0  
> **Last Updated**: 2026-04-26  
> **Author**: Copaw

---

## 📋 概述

CineMate 需要多个第三方 API Key 来实现视频生成功能。本文档说明如何安全地配置和管理这些 API Key。

---

## 🔑 所需 API Key 清单

### 核心服务 (必需)

| 服务 | 环境变量 | 用途 | 成本估算 |
|------|----------|------|----------|
| **Kling AI** | `KLING_API_KEY` | 图像生成视频 (I2V) | ~$0.075/s |
| **Runway ML** | `RUNWAY_API_KEY` | 文本生成视频 (T2V) | ~$0.05/s |
| **DashScope** | `DASHSCOPE_API_KEY` | LLM (Director Agent) + TTS | ~$0.002/1K tokens |

### 可选服务 (Fallback)

| 服务 | 环境变量 | 用途 | 成本估算 |
|------|----------|------|----------|
| **Flux** | `FLUX_API_KEY` | 文本生成图像 (T2I) | ~$0.003/image |
| **Luma AI** | `LUMA_API_KEY` | 图像生成视频 (Fallback) | ~$0.08/s |
| **ElevenLabs** | `ELEVENLABS_API_KEY` | TTS (Fallback) | ~$0.30/1K chars |
| **Stability AI** | `STABILITY_API_KEY` | T2I (Budget) | ~$0.002/image |

---

##  快速开始

### 方式 1: 环境变量 (推荐开发环境)

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export KLING_API_KEY="your-kling-api-key"
export RUNWAY_API_KEY="your-runway-api-key"
export DASHSCOPE_API_KEY="your-dashscope-api-key"

# 生效
source ~/.bashrc  # 或 source ~/.zshrc
```

### 方式 2: .env 文件 (推荐项目环境)

在项目根目录创建 `.env` 文件：

```bash
# .env (不要提交到 Git!)
KLING_API_KEY=your-kling-api-key
RUNWAY_API_KEY=your-runway-api-key
DASHSCOPE_API_KEY=your-dashscope-api-key
FLUX_API_KEY=your-flux-api-key
```

加载 `.env` 文件：

```bash
# 使用 python-dotenv
pip install python-dotenv
```

在代码中加载：

```python
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件
```

### 方式 3: CineMate 配置文件

创建 `cine_mate.yaml` 在项目根目录：

```yaml
models:
  image_to_video:
    primary:
      api_key_env: KLING_API_KEY
  
  text_to_video:
    primary:
      api_key_env: RUNWAY_API_KEY
  
  llm:
    primary:
      api_key_env: DASHSCOPE_API_KEY
```

---

## 📝 获取 API Key 指南

### 1. Kling AI (快手)

**官网**: https://kling.kuaishou.com/

**步骤**:
1. 注册快手开放平台账号
2. 创建应用，获取 API Key
3. 充值账户 (支持支付宝/微信)
4. 在控制台查看 API Key

**定价**:
- 720p: ~$0.075/s
- 1080p: ~$0.15/s
- 首次注册赠送 $5 额度

---

### 2. Runway ML (Gen-4)

**官网**: https://runwayml.com/

**步骤**:
1. 注册 Runway 账号
2. 进入 Settings → API
3. 生成 API Key
4. 绑定信用卡 (国际支付)

**定价**:
- 720p: ~$0.05/s
- 1080p: ~$0.10/s
- 免费额度：125 credits (~$1.25)

---

### 3. DashScope (阿里云通义千问)

**官网**: https://dashscope.aliyun.com/

**步骤**:
1. 注册阿里云账号
2. 开通 DashScope 服务
3. 创建 API Key
4. 实名认证 (国内必需)

**定价**:
- Qwen-Max: ~$0.012/1K tokens
- Qwen-Plus: ~$0.004/1K tokens
- Qwen-Turbo: ~$0.001/1K tokens
- 新用户赠送 ¥1000 额度

---

### 4. Flux (Black Forest Labs)

**官网**: https://blackforestlabs.ai/

**步骤**:
1. 注册账号
2. 进入 Dashboard → API Keys
3. 创建新 Key
4. 绑定支付方式

**定价**:
- Flux Pro 1.1: ~$0.003/image
- 免费额度：100 images/month

---

### 5. Luma AI

**官网**: https://lumalabs.ai/

**步骤**:
1. 注册 Luma 账号
2. 进入 API 页面
3. 生成 API Key
4. 添加信用卡

**定价**:
- Dream Machine: ~$0.08/s
- 免费额度：30 videos/month

---

### 6. ElevenLabs (TTS)

**官网**: https://elevenlabs.io/

**步骤**:
1. 注册账号
2. Profile → API Key
3. 复制 Key
4. 升级套餐 (免费层有限制)

**定价**:
- Starter: $5/month (30K chars)
- Creator: $22/month (100K chars)
- 免费层：10K chars/month

---

## 🔒 安全最佳实践

### ✅ DO (推荐做法)

```bash
# 1. 使用环境变量
export KLING_API_KEY="sk-..."

# 2. 使用 .env 文件 (加入 .gitignore)
echo ".env" >> .gitignore

# 3. 定期轮换 Key
# 每 90 天更新一次 API Key

# 4. 使用最小权限原则
# 为不同环境创建不同的 Key

# 5. 监控使用情况
# 定期检查 API 使用量和费用
```

### ❌ DON'T (避免做法)

```bash
# 1. 不要硬编码在代码中
api_key = "sk-1234567890"  # ❌

# 2. 不要提交到 Git
git add .env  # ❌

# 3. 不要分享 Key
# 不要在聊天/邮件中明文发送

# 4. 不要使用生产 Key 开发
# 为开发环境创建单独的 Key

# 5. 不要超过配额
# 设置使用告警
```

---

## 🧪 测试 API Key

### 测试 Kling API Key

```bash
cd /Users/lianwenhua/indie/Agents/copaw/projects/cineMate

# 设置环境变量
export KLING_API_KEY="your-key-here"

# 运行测试
pytest tests/integration/test_kling_real.py::test_kling_api_key_validation -v

# 或手动测试
python -c "from tests.integration.test_kling_real import manual_kling_test; import asyncio; asyncio.run(manual_kling_test())"
```

### 测试 Runway API Key

```bash
export RUNWAY_API_KEY="your-key-here"

# 运行测试
pytest tests/integration/test_runway_real.py::test_runway_api_key_validation -v

# 或手动测试
python -c "from tests.integration.test_runway_real import manual_runway_test; import asyncio; asyncio.run(manual_runway_test())"
```

---

## 📊 成本估算

### 开发测试 (每日)

| 操作 | 次数 | 单次成本 | 日成本 |
|------|------|----------|--------|
| Kling T2V (5s, 720p) | 10 | $0.375 | $3.75 |
| Runway T2V (4s, 720p) | 10 | $0.20 | $2.00 |
| LLM (Qwen-Max) | 100 | $0.01 | $1.00 |
| **总计** | - | - | **~$6.75/天** |

### 生产环境 (每月)

| 操作 | 次数 | 单次成本 | 月成本 |
|------|------|----------|--------|
| Kling T2V (10s, 720p) | 1000 | $0.75 | $750 |
| Runway T2V (10s, 720p) | 500 | $0.50 | $250 |
| LLM (Qwen-Plus) | 10000 | $0.005 | $50 |
| TTS (CosyVoice) | 1000 | $0.02 | $20 |
| **总计** | - | - | **~$1,070/月** |

---

## 🚨 故障排查

### 问题 1: API Key 无效

**错误**: `ProviderError: API key not set`

**解决**:
```bash
# 检查环境变量
echo $KLING_API_KEY

# 如果为空，重新设置
export KLING_API_KEY="your-key-here"
```

### 问题 2: 配额不足

**错误**: `ProviderError: Insufficient credits`

**解决**:
1. 登录对应平台控制台
2. 查看余额
3. 充值账户

### 问题 3: 网络超时

**错误**: `aiohttp.ClientError: Connection timeout`

**解决**:
```bash
# 检查网络连接
ping api.wavespeed.ai
ping api.runwayml.com

# 检查代理设置
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="http://proxy:port"
```

### 问题 4: 速率限制

**错误**: `ProviderError: Rate limit exceeded`

**解决**:
1. 等待 60 秒后重试
2. 升级 API 套餐
3. 实现指数退避重试

---

## 📚 相关文档

- [CineMate 架构文档](../architecture.md)
- [Provider Adapter 设计](../adr/ADR-003_provider_adapter.md)
- [配置加载器 API](../cine_mate/config/loader.py)

---

## 📞 支持

如有问题，请：
1. 查看 [GitHub Issues](https://github.com/lamwimham/cineMate/issues)
2. 联系 PM: @lamwimham
3. 查阅官方 API 文档

---

**Maintained by**: Copaw  
**Role**: Infra & Skill 负责人  
**Last Review**: 2026-04-26

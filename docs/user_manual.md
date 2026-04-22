# CineMate 用户手册

> **Version**: 1.0.0 (MVP)  
> **Last Updated**: 2026-04-26  
> **适用版本**: v0.1.0

---

## 📖 目录

1. [简介](#简介)
2. [快速开始](#快速开始)
3. [核心功能](#核心功能)
4. [使用指南](#使用指南)
5. [常见问题](#常见问题)
6. [技术支持](#技术支持)

---

## 简介

### 什么是 CineMate？

**CineMate** 是一款 AI 驱动的视频生成工具，帮助视频创作者和导演通过自然语言对话快速生成专业级视频内容。

### 核心特性

- 🎬 **AI 视频生成**: 文本/图像 → 视频
- 💬 **智能对话**: 与 Director Agent 自然交互
-  **Video Git**: 版本管理和回溯
- 📊 **可视化 DAG**: 实时查看生成流程
- 🎨 **多风格支持**: 加载不同导演风格 Skill

### 适用场景

- 短视频创作
- 广告视频制作
- 故事板预览
- 概念视频演示
- 社交媒体内容

---

## 快速开始

### 1. 安装

#### 方式 1: 源码安装 (推荐)

```bash
# 克隆项目
git clone https://github.com/lamwimham/cineMate.git
cd cineMate

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -e .

# 验证安装
cinemate --version
```

#### 方式 2: PyPI 安装 (即将上线)

```bash
pip install cinemate
```

---

### 2. 配置 API Key

CineMate 需要第三方 API Key 来实现视频生成功能。

#### 必需 API Key

| 服务 | 环境变量 | 获取方式 |
|------|----------|----------|
| **Kling AI** | `KLING_API_KEY` | [快手开放平台](https://kling.kuaishou.com/) |
| **Runway ML** | `RUNWAY_API_KEY` | [Runway ML](https://runwayml.com/) |
| **DashScope** | `DASHSCOPE_API_KEY` | [阿里云 DashScope](https://dashscope.aliyun.com/) |

#### 配置方式

**方式 A: 环境变量**

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export KLING_API_KEY="your-kling-api-key"
export RUNWAY_API_KEY="your-runway-api-key"
export DASHSCOPE_API_KEY="your-dashscope-api-key"

# 生效
source ~/.bashrc
```

**方式 B: .env 文件**

在项目根目录创建 `.env` 文件：

```bash
KLING_API_KEY=your-kling-api-key
RUNWAY_API_KEY=your-runway-api-key
DASHSCOPE_API_KEY=your-dashscope-api-key
```

> ⚠️ **注意**: `.env` 文件不要提交到 Git！

---

### 3. 启动应用

#### CLI 模式

```bash
# 启动交互式对话
cinemate chat

# 创建视频项目
cinemate create "A cyberpunk city at night with neon lights"

# 查看项目状态
cinemate status

# 查看 Video Git 历史
cinemate log
```

#### GUI 模式 (推荐)

```bash
# 启动桌面应用
cd ui
npm install
npm run tauri dev
```

---

## 核心功能

### 1. 智能对话创作

与 Director Agent 对话，描述你的视频创意：

```
你：我想创建一个赛博朋克风格的城市夜景视频

Director: 好的！我来帮你创建这个视频。

在开始之前，我想确认几个细节：
1. 视频时长：5 秒、10 秒还是 15 秒？
2. 分辨率：720p 还是 1080p？
3. 是否需要特定的色调（如蓝色、紫色、橙色）？

你：10 秒，1080p，紫色调为主

Director: 完美！我将使用 Kling AI 生成这个视频。
预计成本：约 $0.75

开始生成吗？
```

---

### 2. Video Git 版本管理

每次修改都会创建新版本，支持回溯和比较：

```bash
# 查看版本历史
cinemate log

# 输出示例:
* v3 (HEAD) - Updated lighting to purple tone
* v2 - Changed resolution to 1080p
* v1 - Initial creation: cyberpunk city
```

在 GUI 中，你可以：
- 📊 可视化版本树
- 🔄 恢复到任意版本
- 🔍 比较版本差异

---

### 3. DAG 流程可视化

实时查看视频生成流程：

```
[脚本生成] → [角色设计] → [分镜绘制] → [视频生成] → [后期处理]
   ✅           ✅           🔄           ⏳           ⏳
```

状态说明：
- ✅ 已完成
- 🔄 进行中
- ⏳ 等待中
- ❌ 失败

---

### 4. 多 Provider 支持

支持多个视频生成服务商：

| Provider | 类型 | 成本 | 质量 |
|----------|------|------|------|
| **Kling AI** | I2V/T2V | $0.075/s | ⭐⭐⭐⭐⭐ |
| **Runway ML** | T2V | $0.05/s | ⭐⭐⭐⭐ |
| **Luma AI** | I2V | $0.08/s | ⭐⭐⭐⭐ |

自动Fallback机制：
```
主 Provider (Kling) → Fallback (Luma) → Budget (Minimax)
```

---

## 使用指南

### 场景 1: 从零创建视频

**步骤 1**: 启动应用

```bash
cinemate chat
```

**步骤 2**: 描述创意

```
你：创建一个海滩日落的视频，温暖色调，5 秒

Director: 收到！我将为你创建这个视频。

配置确认:
- 主题：海滩日落
- 色调：温暖 (橙色/金色)
- 时长：5 秒
- 分辨率：720p (默认)
- Provider: Kling AI
- 预估成本：$0.375

开始生成？[Y/n]
```

**步骤 3**: 等待生成

```
Director: 🎬 视频生成中...

[脚本生成] ✅
[分镜绘制] ✅
[视频生成] 🔄 (预计剩余 2 分钟)
```

**步骤 4**: 查看结果

```
Director: ✅ 视频生成完成！

视频 URL: https://...
时长：5 秒
成本：$0.375

需要修改吗？我可以：
1. 调整色调
2. 更改时长
3. 重新生成
4. 导出视频
```

---

### 场景 2: 修改现有视频

**步骤 1**: 选择版本

```bash
cinemate log
# 记住要修改的版本号

cinemate edit v2
```

**步骤 2**: 描述修改

```
你：把色调改成冷色调，蓝色为主

Director: 好的！我将修改 v2 版本。

修改内容:
- 色调：温暖 → 冷色调 (蓝色)
- 保留：其他所有设置

开始重新生成？[Y/n]
```

**步骤 3**: 生成新版本

```
Director: ✅ 修改完成！

新版本：v3
修改内容：色调调整
成本：$0.375

查看 Video Git: cinemate log
```

---

### 场景 3: 使用风格 Skill

**步骤 1**: 查看可用 Skills

```bash
cinemate skills list

# 输出示例:
Available Skills:
- wong_kar_wai (王家卫风格)
- christopher_nolan (诺兰风格)
- wes_anderson (韦斯·安德森风格)
- cyberpunk (赛博朋克风格)
```

**步骤 2**: 加载 Skill

```
你：使用王家卫风格创建一个雨夜街道的视频

Director: 好的！已加载 Skill: wong_kar_wai

Skill 效果:
- 色调：低饱和度，绿色调
- 构图：倾斜角度，前景模糊
- 节奏：慢动作
- 音乐：爵士风格

开始生成？[Y/n]
```

---

### 场景 4: 批量生成

**步骤 1**: 准备脚本列表

创建 `scripts.txt`:

```
一个未来城市的航拍镜头
街道上的人群和飞行器
室内场景，主角对话
```

**步骤 2**: 批量生成

```bash
cinemate batch scripts.txt --output ./videos
```

**步骤 3**: 查看结果

```
生成进度:
[1/3] ✅ 未来城市 - $0.75
[2/3] ✅ 街道人群 - $0.75
[3/3] 🔄 室内场景 - 生成中...

总成本：$2.25
```

---

## 常见问题

### Q1: API Key 无效？

**错误**: `ProviderError: API key not set`

**解决**:
```bash
# 检查环境变量
echo $KLING_API_KEY

# 如果为空，重新设置
export KLING_API_KEY="your-key-here"
```

---

### Q2: 生成失败？

**错误**: `ProviderError: Insufficient credits`

**解决**:
1. 登录对应平台控制台
2. 查看余额
3. 充值账户

---

### Q3: 生成速度慢？

**原因**: 视频生成需要时间 (通常 2-5 分钟)

**建议**:
- 使用较短时长 (5 秒 vs 10 秒)
- 选择 720p 而非 1080p
- 避开高峰期

---

### Q4: 如何导出视频？

**CLI 方式**:
```bash
cinemate export v3 --output ./my_video.mp4
```

**GUI 方式**:
1. 在 Video Canvas 中点击视频
2. 点击右上角下载按钮
3. 选择保存位置

---

### Q5: 成本如何计算？

**公式**: `成本 = 时长 (秒) × 单价`

| Provider | 720p 单价 | 1080p 单价 |
|----------|----------|----------|
| Kling AI | $0.075/s | $0.15/s |
| Runway ML | $0.05/s | $0.10/s |
| Luma AI | $0.08/s | $0.16/s |

**示例**:
- Kling 720p 5 秒 = $0.375
- Kling 1080p 10 秒 = $1.50

---

### Q6: 支持哪些语言？

**支持语言**:
- 🇨 中文 (推荐)
- 🇺🇸 英文
- 🇯🇵 日文
- 🇰🇷 韩文

Director Agent 会自动识别并使用相同语言回复。

---

### Q7: 视频版权归属？

**答案**: 生成的视频版权归**用户所有**。

CineMate 仅作为工具提供商，不主张任何版权。但请注意：
- 使用的 Prompt 不应侵犯他人版权
- 生成的内容需遵守当地法律法规

---

## 技术支持

### 获取帮助

1. **文档**: [docs/](../docs/)
2. **Issues**: [GitHub Issues](https://github.com/lamwimham/cineMate/issues)
3. **讨论**: [GitHub Discussions](https://github.com/lamwimham/cineMate/discussions)

### 报告 Bug

请按以下格式报告 Bug：

```markdown
**问题描述**: 简短描述问题

**复现步骤**:
1. ...
2. ...
3. ...

**期望行为**: 应该发生什么

**实际行为**: 实际发生了什么

**环境**:
- OS: macOS/Windows/Linux
- Python: 3.10/3.11/3.12
- CineMate: v0.1.0

**日志**:
[粘贴相关日志]
```

### 功能建议

欢迎提出新功能建议！请说明：
- 功能描述
- 使用场景
- 优先级 (P0/P1/P2)

---

## 附录

### A. 命令行参考

```bash
cinemate --help
cinemate chat
cinemate create <prompt>
cinemate status [run_id]
cinemate log [run_id]
cinemate edit <version>
cinemate export <version> --output <path>
cinemate skills list
cinemate skills load <skill_name>
```

### B. 配置文件示例

```yaml
# cine_mate.yaml
models:
  image_to_video:
    primary:
      provider: kling
      model_name: kling-v2
  text_to_video:
    primary:
      provider: runway
      model_name: runway-gen3

infra:
  redis_url: "redis://localhost:6379"
  db_path: "./cinemate.db"

app:
  log_level: "INFO"
  enable_telemetry: false
```

### C. 快捷键 (GUI)

| 快捷键 | 功能 |
|--------|------|
| `Cmd/Ctrl + N` | 新建项目 |
| `Cmd/Ctrl + S` | 保存 |
| `Cmd/Ctrl + Z` | 撤销 |
| `Cmd/Ctrl + Y` | 重做 |
| `Space` | 播放/暂停 |
| `←/→` | 上一帧/下一帧 |

---

**Maintained by**: CineMate Team  
**Contact**: [GitHub Issues](https://github.com/lamwimham/cineMate/issues)  
**Last Updated**: 2026-04-26

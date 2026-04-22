# CineMate MVP Demo Script

> **Version**: 1.0.0  
> **Duration**: ~3 分钟  
> **Purpose**: Sprint 4 Demo 演示

---

## 🎬 Demo 流程

### 开场 (0:00 - 0:30)

**画面**: CineMate 主界面 (Chat + Canvas)

**旁白**:
```
大家好，这是 CineMate MVP 版本演示。
CineMate 是一款 AI 驱动的视频生成工具，
帮助创作者通过自然对话快速生成专业视频。
```

---

### 场景 1: 创建视频 (0:30 - 1:30)

**画面**: Chat 面板输入

**操作**:
1. 在 Chat 输入框输入：
   ```
   创建一个赛博朋克城市夜景的视频，紫色调，10 秒
   ```

2. Director Agent 回复确认信息

3. 点击"确认生成"按钮

**旁白**:
```
用户只需用自然语言描述创意，
Director Agent 会自动确认细节并开始生成。
```

---

### 场景 2: 查看进度 (1:30 - 2:00)

**画面**: DAG 节点状态图

**操作**:
1. 展示 DAG 流程可视化
2. 节点状态动画：⏳ →  → ✅

**旁白**:
```
生成过程中，用户可以实时查看进度。
DAG 可视化显示每个节点的状态，
从脚本生成到最终视频输出。
```

---

### 场景 3: Video Git (2:00 - 2:30)

**画面**: Video Git 版本树

**操作**:
1. 展示版本历史
2. 点击不同版本预览
3. 演示版本对比

**旁白**:
```
Video Git 功能记录每次修改，
支持版本回溯和对比。
就像 Git 管理代码一样管理视频版本。
```

---

### 场景 4: 修改视频 (2:30 - 3:00)

**画面**: Chat 面板 + Canvas

**操作**:
1. 输入修改请求：
   ```
   把色调改成冷色调，蓝色为主
   ```

2. 展示新版本生成

**旁白**:
```
修改视频同样简单，
只需告诉 Director Agent 你的需求，
系统会自动创建新版本。
```

---

### 结尾 (3:00 - 3:30)

**画面**: CineMate Logo + GitHub 链接

**旁白**:
```
这就是 CineMate MVP 版本的核心功能。
感谢观看！

GitHub: github.com/lamwimham/cineMate
```

---

## 📋 录制清单

### 准备工作

- [ ] 清理桌面，关闭无关应用
- [ ] 设置屏幕分辨率 1920x1080
- [ ] 准备测试 API Key
- [ ] 预生成一个示例视频 (避免等待)
- [ ] 关闭系统通知

### 录制设置

- [ ] 录制软件：OBS / QuickTime
- [ ] 分辨率：1920x1080
- [ ] 帧率：30fps
- [ ] 格式：MP4
- [ ] 音频：系统音频 + 麦克风

### 录制后处理

- [ ] 剪辑多余部分
- [ ] 添加字幕 (可选)
- [ ] 添加背景音乐 (可选)
- [ ] 导出 MP4 (H.264)
- [ ] 上传到 GitHub Releases

---

## 🎥 分镜脚本

### Shot 1: 主界面 (10s)

```
镜头：全景
内容：Chat + Canvas 分屏布局
字幕：CineMate MVP
```

### Shot 2: 输入 Prompt (15s)

```
镜头：特写 Chat 输入框
内容：打字动画
字幕：自然语言创作
```

### Shot 3: DAG 可视化 (20s)

```
镜头：特写 DAG 区域
内容：节点状态变化动画
字幕：实时进度追踪
```

### Shot 4: Video Git (20s)

```
镜头：特写 GitPanel
内容：版本树展开/收起
字幕：版本管理
```

### Shot 5: 修改视频 (20s)

```
镜头：分屏对比
内容：v2 vs v3 对比
字幕：快速迭代
```

### Shot 6: 结尾 (15s)

```
镜头：Logo 动画
内容：GitHub 链接
字幕：github.com/lamwimham/cineMate
```

---

## 💡 演示技巧

### Do (推荐)

- ✅ 提前排练 2-3 遍
- ✅ 使用预生成视频避免等待
- ✅ 保持鼠标移动流畅
- ✅ 语速适中，清晰
- ✅ 展示核心功能即可

### Don't (避免)

- ❌ 现场调试代码
- ❌ 展示错误/失败场景
- ❌ 过长等待时间
- ❌ 过多技术细节
- ❌ 偏离主线功能

---

## 📊 演示环境检查

### 系统检查

```bash
# 检查 Python 环境
python --version  # 3.13.3
pip list | grep cine-mate

# 检查 Redis
redis-cli ping  # PONG

# 检查 API Key
echo $KLING_API_KEY
echo $RUNWAY_API_KEY
echo $DASHSCOPE_API_KEY
```

### UI 检查

```bash
cd ui
npm run dev  # 确保无错误

# 检查浏览器
# Chrome: http://localhost:5173
```

### 数据检查

```bash
# 清理旧数据 (可选)
rm cinemate.db
rm -rf cinemate_cas

# 创建示例项目
cinemate create "Demo video for sprint 4"
```

---

## 🎬 录制时间表

| 时间 | 任务 | 负责人 |
|------|------|--------|
| Sprint 4 Day 4 | 准备 Demo 环境 | Copaw |
| Sprint 4 Day 5 | 录制 Demo 视频 | Claude |
| Sprint 4 Day 6 | 后期处理 | Claude |
| Sprint 4 Day 6 | Sprint Review Demo | PM |

---

## 📤 交付物

- [ ] Demo 视频 MP4 (3 分钟)
- [ ] Demo GIF (30 秒，用于 README)
- [ ] 截图 (5-10 张)
- [ ] Demo Script 文档

---

**Maintained by**: Copaw  
**Last Updated**: 2026-04-26

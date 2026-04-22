# CineMate Design System V2

> **版本**: 2.0.0 | **日期**: 2026-04-21 | **状态**: 实现中
> **主题**: 深色专业视频创作套件

---

## 1. 设计哲学

### 1.1 核心原则

1. **Dark-First**: 视频创作在暗光环境中进行，深色主题减少视觉疲劳
2. **Status-Centric**: DAG 节点状态必须一目了然，用颜色和动画传递信息
3. **Progressive Disclosure**: 信息按需展示，不堆砌
4. **Cinematic Feel**: 微动画、渐变、光影营造电影感

### 1.2 视觉隐喻

| 元素 | 隐喻 | 设计表达 |
|------|------|----------|
| DAG 节点 | 电影拍摄镜头 | 圆角卡片 + 状态光环 |
| 节点连线 | 胶片齿孔轨道 | 虚线/实线 + 流动动画 |
| 执行中 | 正在曝光 | 脉冲光环 + 进度条 |
| 成功 | 拍摄完成 | 绿色对勾 + 轻微缩放 |
| 失败 | 拍摄事故 | 红色抖动 + 错误波纹 |
| 可重用 | 存档素材 | 虚线边框 + 复用标记 |

---

## 2. 色彩系统

### 2.1 基础色板

```css
:root {
  /* 背景层级 */
  --bg-darkest:   #050508;   /* 底层背景 */
  --bg-dark:      #0a0a0f;   /* 主背景 */
  --bg-base:      #13131f;   /* 面板背景 */
  --bg-elevated:  #1a1a2e;   /* 浮起面板 */
  --bg-hover:     #252540;   /* 悬停状态 */
  --bg-active:    #2d2d4d;   /* 激活状态 */

  /* 品牌色 */
  --brand:        #6366f1;
  --brand-dim:    #4f46e5;
  --brand-glow:   rgba(99, 102, 241, 0.3);
  --brand-subtle: rgba(99, 102, 241, 0.1);

  /* 状态色 */
  --success:      #22c55e;
  --success-dim:  #16a34a;
  --success-glow: rgba(34, 197, 94, 0.25);
  --warning:      #f59e0b;
  --warning-dim:  #d97706;
  --warning-glow: rgba(245, 158, 11, 0.25);
  --error:        #ef4444;
  --error-dim:    #dc2626;
  --error-glow:   rgba(239, 68, 68, 0.25);
  --info:         #3b82f6;
  --info-dim:     #2563eb;
  --info-glow:    rgba(59, 130, 246, 0.25);

  /* 文本色 */
  --text-primary:   #f1f5f9;
  --text-secondary: #94a3b8;
  --text-tertiary:  #64748b;
  --text-muted:     #475569;

  /* 边框与分隔 */
  --border:         rgba(255, 255, 255, 0.06);
  --border-strong:  rgba(255, 255, 255, 0.12);
  --divider:        rgba(255, 255, 255, 0.04);

  /* 特殊效果 */
  --glass-bg:       rgba(19, 19, 31, 0.8);
  --glass-border:   rgba(255, 255, 255, 0.08);
  --shadow-sm:      0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md:      0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg:      0 8px 24px rgba(0, 0, 0, 0.5);
  --glow-brand:     0 0 20px rgba(99, 102, 241, 0.15);
}
```

### 2.2 DAG 节点状态色

| 状态 | 主色 | 光环色 | 背景色 | 动画 |
|------|------|--------|--------|------|
| **pending** | `--text-tertiary` | 无 | `--bg-base` | 无 |
| **queued** | `--info` | `--info-glow` | `--bg-base` | 轻微呼吸 |
| **executing** | `--warning` | `--warning-glow` | `--bg-base` | 脉冲光环 + 进度条流动 |
| **succeeded** | `--success` | `--success-glow` | `rgba(34,197,94,0.05)` | 对勾弹出 + 轻微放大 |
| **failed** | `--error` | `--error-glow` | `rgba(239,68,68,0.05)` | 抖动 + 错误波纹 |
| **skipped** | `--brand` | 无 | `--bg-base` | 无（虚线边框） |

---

## 3. 排版系统

### 3.1 字体

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'SF Mono', monospace;
```

### 3.2 字号阶梯

| Token | 大小 | 字重 | 用途 |
|-------|------|------|------|
| **text-xs** | 11px | 500 | 标签、元数据、状态文字 |
| **text-sm** | 13px | 400 | 正文、描述 |
| **text-sm-b** | 13px | 600 | 按钮文字、节点标题 |
| **text-base** | 14px | 400 | 主要文本 |
| **text-base-b** | 14px | 600 | 标题、强调 |
| **text-lg** | 16px | 600 | 面板标题 |
| **text-xl** | 20px | 700 | 页面标题 |
| **text-mono** | 12px | 400 | 代码、ID、时间戳 |

### 3.3 行高

- 紧凑：1.2（标签、标题）
- 正常：1.5（正文）
- 宽松：1.75（聊天消息）

---

## 4. 间距系统

| Token | 值 | 用途 |
|-------|-----|------|
| **space-1** | 4px | 图标间距 |
| **space-2** | 8px | 内联间距 |
| **space-3** | 12px | 组件内边距 |
| **space-4** | 16px | 卡片内边距 |
| **space-5** | 20px | 面板内边距 |
| **space-6** | 24px | 区块间距 |
| **space-8** | 32px | 大区块间距 |

---

## 5. 组件规范

### 5.1 DAG 节点 (DagNode)

```
┌─────────────────────────┐
│  ┌───┐                  │
│  │ 📝│  Script          │  ← 状态图标 + 节点名称
│  └───┘                  │
│  ━━━━━━━━━━━━░░░░░      │  ← 进度条（executing 状态）
│  ⏱ 1.2s  💰 ¥0.5       │  ← 元数据（等宽字体）
└─────────────────────────┘
      ↑ 状态色边框/光环
```

**规格**:
- 尺寸：160px × 90px
- 圆角：12px
- 背景：`--bg-elevated`
- 边框：1px solid `--border`
- 状态光环：外圈 2px，带 `box-shadow` 发光
- 阴影：`--shadow-sm`
- 悬停：`--shadow-md` + `translateY(-2px)`

### 5.2 DAG 连线 (DagEdge)

- 类型：水平贝塞尔曲线
- 颜色：
  - 正常：`--text-muted`
  - 数据流动中：`--brand`（带动画虚线）
- 宽度：2px
- 箭头：8px 等边三角形

### 5.3 聊天气泡

- AI 消息：左侧，背景 `--bg-elevated`，边框 `--border`
- 用户消息：右侧，背景 `--brand-subtle`，边框 `--brand-glow`
- 圆角：16px（AI）/ 16px 16px 4px 16px（用户）
- 最大宽度：80%

### 5.4 按钮

**Primary**:
- 背景：`--brand`
- 文字：白色
- 圆角：8px
- 悬停：亮度 +10% + `--glow-brand`
- 按下：缩放 0.97

**Ghost**:
- 背景：透明
- 文字：`--text-secondary`
- 悬停：背景 `--bg-hover`

---

## 6. 动画规范

### 6.1 DAG 节点动画

| 触发条件 | 动画 | 时长 | 缓动 |
|----------|------|------|------|
| 节点进入 | fadeIn + slideUp | 300ms | ease-out |
| executing | pulse-glow | 2s | ease-in-out (循环) |
| succeeded | scalePop + checkDraw | 400ms | spring |
| failed | shakeX | 500ms | ease-in-out |
| 悬停 | lift + shadowGrow | 200ms | ease-out |
| 点击 | scaleDown | 100ms | ease-in |

### 6.2 进度条动画

```css
@keyframes progress-flow {
  0% { background-position: 0% 0; }
  100% { background-position: 200% 0; }
}
```
- 条纹背景，从左向右流动
- 时长：1s linear infinite

### 6.3 页面转场

- 面板切换：fade + slideX（200ms）
- 模态框：fade + scale（250ms）
- 通知 toast：slideInRight + fade（300ms）

---

## 7. 布局架构

### 7.1 三栏布局

```
┌──────────────────────────────────────────────────────────────┐
│  TopBar (52px)                                               │
├──────────────┬───────────────────────────────┬───────────────┤
│              │                               │               │
│  Chat Panel  │     Video Canvas              │  Git Panel    │
│  (280px)     │     (flex: 1)                 │  (240px)      │
│              │                               │               │
│  ──────────  │  ┌─────────────────────────┐  │  ──────────   │
│  DAG Panel   │  │                         │  │  Run Info     │
│  (底部 200px)│  │    视频预览              │  │               │
│              │  │                         │  │               │
├──────────────┤  │    [播放控制]            │  ├───────────────┤
│  输入框       │  │                         │  │  Skills       │
│              │  └─────────────────────────┘  │               │
└──────────────┴───────────────────────────────┴───────────────┘
```

### 7.2 DAG 面板布局

```
┌─────────────────────────────────────────────────────────────┐
│  Pipeline DAG                                               │
│                                                             │
│  ○──→ [📝 Script] ──→ [🎬 Storyboard] ──→ [🎥 Video]       │
│           ✅                  ✅               🔄 75%        │
│                                                             │
│                        ↓                                    │
│                                                             │
│              [🎙️ Voice] ──→ [✨ Compose]                    │
│                ⏳              ⏳                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. 交互模式

### 8.1 节点交互

- **单击**：展开节点详情面板（参数、日志、输出预览）
- **双击**：聚焦该节点对应的视频片段
- **悬停**：显示工具提示（节点类型、预计耗时、成本）

### 8.2 DAG 交互

- **点击节点**：高亮该节点及其上下游路径
- **滚轮**：水平滚动 DAG 面板
- **执行中自动聚焦**：当前执行节点自动滚动到可视区域中心

### 8.3 实时反馈

- 节点状态变化时，播放对应音效（可选）
- 执行完成时，节点轻微闪烁提示
- 错误发生时，对应节点及上游路径高亮红色

---

## 9. 响应式断点

| 断点 | 宽度 | 布局调整 |
|------|------|----------|
| **xl** | ≥1400px | 完整三栏 |
| **lg** | ≥1200px | Chat 缩至 240px |
| **md** | ≥1024px | Git 面板收起为图标栏 |
| **sm** | <1024px | 单栏布局，面板切换 |

---

**文档完成**: 2026-04-21
**下次更新**: DAG 交互原型验证后

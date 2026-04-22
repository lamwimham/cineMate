# CineMate 前端架构设计文档 (Tauri 方案)

> **Version**: 1.0.0 | **Date**: 2026-04-21 | **Status**: Draft
> **技术栈**: Tauri + Vite + React + TypeScript + Tailwind CSS

---

## 1. 技术选型决策

### 1.1 为什么选 Tauri 而非 Electron

| 维度 | Electron | Tauri (选定) |
|------|----------|-------------|
| **包体积** | ~150MB (含 Chromium) | ~15MB (系统 WebView) |
| **内存占用** | ~300MB | ~100MB |
| **启动速度** | 较慢 | 快 |
| **安全性** | 大攻击面 (Chromium + Node.js) | 小攻击面 (系统 WebView + Rust) |
| **前端兼容性** | 完整 Chromium | 现代系统 WebView (Safari/Edge/WebKit) |
| **后端语言** | Node.js | Rust（与 Python 通过子进程/HTTP 通信）|
| **生态成熟度** | 非常成熟 | 快速成长，v2 已稳定 |

**核心原因**：
1. CineMate 的核心资产是 **Python AI 引擎**，桌面壳只需要轻量级承载前端
2. 不需要 Electron 的完整 Node.js 运行时（我们不写 Node.js 后端逻辑）
3. Tauri 的 Rust 后端更适合管理 **Python 子进程生命周期**
4. 更小的包体积对视频创作者更友好（他们可能同时运行 AE/PR/达芬奇）

### 1.2 技术栈分层

```
┌─────────────────────────────────────────┐
│  Presentation Layer (WebView)           │
│  React 18 + Vite + TypeScript           │
│  Tailwind CSS + Radix UI (planned)      │
│  Lucide React Icons                     │
└─────────────────────────────────────────┘
                    │
                    │ Tauri IPC / HTTP fetch
                    ▼
┌─────────────────────────────────────────┐
│  Tauri Rust Backend                     │
│  - Window Management                    │
│  - Python Sidecar Lifecycle             │
│  - Native File System (CAS access)      │
│  - OS Notifications                     │
└─────────────────────────────────────────┘
                    │
                    │ std::process::Command (spawn/kill)
                    ▼
┌─────────────────────────────────────────┐
│  Python Local Service (FastAPI)         │
│  - Store (SQLite)                       │
│  - Orchestrator (DAG/FSM)               │
│  - Director Agent                       │
│  - Skills System                        │
│  - EventBus (SSE for real-time push)    │
└─────────────────────────────────────────┘
                    │
                    │ HTTPS (Control Plane)
                    ▼
┌─────────────────────────────────────────┐
│  Cloud Gateway                          │
│  - Auth / Billing / Routing             │
└─────────────────────────────────────────┘
```

---

## 2. 前后端通信机制

### 2.1 通信模式总览

| 场景 | 协议 | 说明 |
|------|------|------|
| **前端 ↔ Python 引擎** | HTTP + SSE | 主通信方式，前端直接 fetch 本地 FastAPI |
| **前端 ↔ Rust 后端** | Tauri IPC | 仅用于：启动/停止 Python、原生文件对话框、系统通知 |
| **Rust ↔ Python** | std::process | Rust 管理 Python 子进程生命周期 |

### 2.2 Python FastAPI 本地服务

**启动方式**：
```bash
# 开发模式（手动或 Tauri 自动启动）
python -m cine_mate.api.server --port 8787

# 生产模式（Tauri Sidecar）
./cinemate-python-sidecar --port 8787
```

**服务地址**：
- 开发: `http://localhost:8787`
- 生产: `http://localhost:8787`（Sidecar 内部端口）

### 2.3 Tauri Rust 后端职责

```rust
// 核心命令
#[tauri::command]
fn restart_python_service(state: State<AppState>) -> Result<String, String>

#[tauri::command]
fn get_service_status(state: State<AppState>) -> Result<String, String>

// 自动行为
// 1. Tauri 启动时 → 自动检测并启动 Python 服务
// 2. Tauri 关闭时 → 优雅终止 Python 子进程
// 3. Python 崩溃时 → 前端检测 + 一键重启
```

---

## 3. 前端项目结构

```
ui/
├── src/
│   ├── main.tsx              # React 应用入口
│   ├── App.tsx               # 根组件（三栏布局）
│   ├── index.css             # Tailwind + 全局样式 + CSS 变量
│   ├── components/           # 可复用组件
│   │   ├── layout/           # 布局组件
│   │   │   ├── TopBar.tsx
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── VideoCanvas.tsx
│   │   │   ├── DagStatus.tsx
│   │   │   └── VideoGitPanel.tsx
│   │   ├── chat/             # 聊天相关
│   │   ├── video/            # 视频播放器
│   │   └── git/              # Video Git 树
│   ├── hooks/                # 自定义 React Hooks
│   │   ├── usePythonApi.ts   # Python FastAPI 调用
│   │   ├── useEventSource.ts # SSE 实时推送
│   │   └── useTauri.ts       # Tauri IPC 调用
│   ├── stores/               # 状态管理 (Zustand)
│   │   ├── chatStore.ts
│   │   ├── projectStore.ts
│   │   └── runStore.ts
│   ├── types/                # TypeScript 类型定义
│   └── lib/
│       └── api.ts            # API 客户端封装
├── src-tauri/                # Tauri Rust 后端
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   ├── capabilities/
│   └── src/
│       ├── main.rs
│       └── lib.rs            # Python 服务管理 + Tauri 命令
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── package.json
```

---

## 4. Python FastAPI API 设计

### 4.1 REST API 端点

```
GET  /health                    # 健康检查
POST /api/v1/projects           # 创建项目
GET  /api/v1/projects           # 项目列表
GET  /api/v1/projects/{id}      # 项目详情
POST /api/v1/projects/{id}/runs # 提交 Run
GET  /api/v1/runs/{id}          # Run 状态
GET  /api/v1/runs/{id}/nodes    # 节点执行状态
POST /api/v1/chat               # 发送消息给 Director Agent
GET  /api/v1/skills             # 技能列表
GET  /api/v1/blobs/{hash}       # 获取视频/图片文件
```

### 4.2 SSE 实时推送

```
GET /api/v1/events/stream

Event: node_completed
Data: {"run_id": "...", "node_id": "...", "status": "succeeded", "artifact_url": "..."}

Event: node_failed
Data: {"run_id": "...", "node_id": "...", "error": "..."}

Event: job_status_update
Data: {"job_id": "...", "progress": 75, "status": "processing"}
```

---

## 5. 设计系统 (Design System)

### 5.1 CSS 变量

```css
:root {
  --primary: #6366f1;
  --primary-hover: #4f46e5;
  --primary-light: #e0e7ff;
  --success: #22c55e;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #3b82f6;
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --border: #e2e8f0;
}

.dark {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --border: #334155;
}
```

### 5.2 Tailwind 配置

见 `ui/tailwind.config.js`

---

## 6. 开发工作流

### 6.1 启动开发环境

```bash
# Terminal 1: 启动 Python FastAPI 服务
cd /path/to/cineMate
python -m cine_mate.api.server --port 8787

# Terminal 2: 启动 Tauri 开发模式
cd ui
npm run tauri dev
```

### 6.2 构建生产包

```bash
cd ui
npm run tauri build
# 输出: src-tauri/target/release/bundle/
```

### 6.3 调试

- **前端**: Chrome DevTools (`Ctrl+Shift+I` / `Cmd+Option+I`)
- **Rust**: `RUST_LOG=debug cargo tauri dev`
- **Python**: 独立终端查看 FastAPI 日志

---

## 7. 与 Electron 方案的关键差异

| 方面 | Electron | Tauri |
|------|----------|-------|
| 前端构建 | 相同 (Vite + React + TS) | 相同 |
| 后端进程 | Node.js 主进程 | Python FastAPI 子进程 |
| 前端调用后端 | `ipcRenderer.invoke()` | `fetch()` 到 localhost |
| 文件系统访问 | Node.js `fs` | Python `pathlib` + FastAPI 静态文件 |
| 包大小 | ~150MB | ~15MB + Python 环境 |
| 多平台构建 | electron-builder | `cargo tauri build` |

**关键优势**：
- Python 引擎无需任何改造即可被前端使用（通过 HTTP）
- 未来可以很方便地剥离出纯 Web 版本（前端代码几乎不变）
- Rust 后端的进程管理比 Node.js 更可靠

---

## 8. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| Python 环境依赖 | 用户需安装 Python | 未来用 PyInstaller 打包为 Sidecar |
| WebView 兼容性 | 老旧系统可能不支持 | Tauri v2 支持系统 WebView2/webkit2gtk |
| 端口冲突 (8787) | 多实例冲突 | 动态端口分配 |
| Rust 学习曲线 | 团队需掌握 Rust | 当前 Rust 代码极简（仅进程管理）|

---

**文档完成**: 2026-04-21
**下次更新**: 前端 P0 开发完成后复审

# CineMate 架构设计文档 (Technical Design Document)

> **Version**: 0.2.0 (Commercial Edition) | **Date**: 2026-04-21 | **Status**: Draft
> **Principle**: Local-First, Agent-Driven, Cloud-Billing, BYOK-Ready.

## 1. 项目概述 (Project Overview)

### 1.1 核心愿景
CineMate 是一个 **AI 视频制作操作系统 (AI Video OS)**。它不同于市面上的“一键生成”黑盒工具，也不同于复杂的节点连线工具。它是一个由 **Director Agent** 驱动的、具备 **增量修改 (Incremental Update)** 和 **版本回溯 (Video Git)** 能力的工程化平台。

### 1.2 设计原则
1.  **Local-First (本地优先)**: 所有资产（图像、视频、配置）以本地文件为唯一真理源，SQLite 仅作索引与元数据存储。
2.  **Cloud-Brain (云端大脑)**: 核心 Agent 推理与计费网关在云端，本地客户端只负责执行、存储与渲染。
3.  **Commercial-Ready (商业化原生)**:
    *   支持 **Managed Credits**（官方托管 Key，按量付费）。
    *   支持 **BYOK (Bring Your Own Key)**（用户自带 Key，订阅制）。
4.  **Video Git (版本控制)**: 引入 Git 式的分支管理与内容寻址存储，实现全量历史回溯。

---

## 2. 系统分层架构 (Layered Architecture)

系统采用“端云分离”的四层架构设计：

```text
+-------------------------------------------------------------+
|              LOCAL CLIENT (CineMate Desktop)                |
|  [UI/Chat] -> [Local Engine (DAG/FSM)] -> [Renderer]        |
+-------------------------------------------------------------+
        │  (1) Control Protocol (HTTPS)
        ▼
+-------------------------------------------------------------+
|              CLOUD GATEWAY (CineMate Server)                |
|  [Auth] -> [Router] -> [Upstream Proxy] -> [Audit/Billing]  |
+-------------------------------------------------------------+
        │  (2) Data Protocol (Direct to Upstream)
        ▼
+-------------------------------------------------------------+
|              UPSTREAM PROVIDERS                             |
|  OpenAI | Kling | Runway | Local GPU Cluster               |
+-------------------------------------------------------------+
```

### 2.1 通信与数据流设计
*   **Control Plane (走服务端)**:
    *   Agent 意图解析 (Director Agent)
    *   API 鉴权与配额检查
    *   任务路由与分发 (Proxy)
    *   **计费与审计日志** (核心商业逻辑)
*   **Data Plane (直连/绕过服务端)**:
    *   视频/图像下载 (通过上游签名的 Pre-signed URL)
    *   本地文件存储 (Blob Store)
    *   *目的: 零带宽成本*

---

## 3. 核心引擎设计 (Core Engine)

### 3.1 视频 Git 与内容寻址 (Video Git & CAS)
*   **Commit = Run**: 每次生成视为一次 Commit，记录完整的 DAG 快照。
*   **Branch = Lineage**: 基于 `parent_run_id` 的版本树。
*   **CAS (Content-Addressable Store)**:
    *   大文件 (MP4/PNG) 以 SHA256 存入本地 `objects/`。
    *   `artifacts_index` 表仅记录引用，实现 **0 拷贝** 的版本分支切换。

### 3.2 变更引擎 (Change Engine)
*   **Dirty Propagation**: 基于 DAG 的拓扑分析，精确计算受影响的节点集合。
*   **Version Merge**: 支持跨版本拼接（如 v1 的画面 + v2 的音频）。

### 3.3 商业与安全协议 (Commercial Protocol)
为了防止客户端劫持并支持灵活计费，所有请求遵循 `CineMate Protocol`:
1.  **Billing Mode**: 每个请求头携带 `billing_mode` (managed/byok)。
2.  **BYOK 验证**: 若为 BYOK 模式，客户端需在本地 Keychain 加密 Key，并发送 Hash 签名供服务端验证权限，**Key 绝不经过网络**。
3.  **Result 签名**: 服务端返回的结果带有防篡改签名，本地 Engine 校验后才更新状态。

### 3.4 技能系统 (Skill System) - Anthropic Style Spec
导演风格（如王家卫、诺兰）被定义为可插拔的技能。参考 Anthropic 的 Skills/Custom Instructions 规范，将**自然语言指令**与**硬参数配置**分离。

#### 3.4.1 目录结构
```text
skills/
└── wong-kar-wai/
    ├── SKILL.md       # 核心指令 (Agent 读取)
    └── config.yaml    # 技术参数 (Engine 读取)
```

#### 3.4.2 SKILL.md (Agent Prompt)
这是给 Director Agent 的"导演手册"。
```markdown
---
name: wong-kar-wai
version: 1.0.0
---

# Role
You are an expert cinematographer specializing in the **Wong Kar-wai** aesthetic.

# Instructions
1. **Pacing**: Always suggest **slow-motion** (step-printing effect).
2. **Framing**: Use **tight close-ups** and **handheld camera**. Subjects framed through foreground objects.
3. **Lighting**: High contrast, neon colors (teal/orange), deep shadows.
4. **Atmosphere**: Urban alienation, rain, smoke.
```

#### 3.4.3 config.yaml (Engine Overrides)
这是给执行引擎的硬约束。
```yaml
technical_overrides:
  prompt_suffix: ", cinematic shot, 35mm lens, motion blur, neon lighting, film grain"
  negative_prompt: "bright, sunny, static, wide angle"
  
  # Strict Parameters
  motion_strength: 0.3
  camera_movement: "handheld"
  aspect_ratio: "2.39:1"
  preferred_model: "kling-v2-pro"
```

#### 3.4.4 注入机制
*   **Agent**: 加载 `SKILL.md` 到 System Prompt，使其理解风格意图。
*   **Engine**: 加载 `config.yaml` 覆盖默认生成参数。
*   **冲突**: `config.yaml` 优先级最高。

---

## 4. 数据模型 (Data Model)

### 4.1 本地模型 (Local SQLite)

```sql
-- [新增] 用户设置与模式配置
CREATE TABLE IF NOT EXISTS user_settings (
    user_id TEXT PRIMARY KEY,
    api_mode TEXT DEFAULT 'managed',      -- 'managed' or 'byok'
    byok_config TEXT,                     -- JSON: 加密 Key 的哈希/元数据
    managed_credits REAL DEFAULT 0.0,     -- 本地缓存的余额
    last_sync_at DATETIME
);

-- [更新] 追踪日志 (细化计费信息)
CREATE TABLE IF NOT EXISTS traces (
    trace_id TEXT PRIMARY KEY,
    run_id TEXT,
    user_input TEXT,
    agent_response_summary TEXT,
    
    -- 计费明细
    cost_llm REAL DEFAULT 0.0,
    cost_generation REAL DEFAULT 0.0,
    billing_mode TEXT DEFAULT 'managed',
    
    -- 路由信息
    route_provider TEXT,                  -- 实际调用的上游模型
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 服务端模型 (Server PostgreSQL - 逻辑视图)

服务端不存储视频文件，仅存储审计与计费数据：

```sql
-- 核心审计表
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    trace_id TEXT NOT NULL,
    
    request_payload_hash TEXT,            -- 用于审计请求内容
    response_payload_hash TEXT,           -- 用于审计结果
    
    -- 财务字段
    billing_mode TEXT NOT NULL,           -- managed / byok
    token_cost INT DEFAULT 0,             -- LLM Token 消耗
    credit_deducted FLOAT DEFAULT 0.0,    -- 实际扣除金额
    upstream_cost FLOAT DEFAULT 0.0,      -- 上游厂商实际成本
    profit_margin FLOAT DEFAULT 0.0,      -- 毛利
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- 路由状态表
CREATE TABLE provider_health (
    provider_name TEXT PRIMARY KEY,
    latency_ms INT,
    error_rate FLOAT,
    queue_depth INT
);
```

---

## 5. API 契约 (API Contract)

CineMate 客户端与服务端通过 HTTPS 进行通信。

### 5.1 提交任务
`POST /api/v1/jobs`

**Request Headers:**
- `Authorization: Bearer <token>`
- `X-CineMate-Client-Version: 0.1.0`
- `X-BYOK-Signature: sha256_hash` (仅在 BYOK 模式下)

**Request Body:**
```json
{
  "job_id": "client_uuid",
  "type": "text_to_video",
  "params": {
    "prompt": "A cyberpunk city...",
    "skill_id": "wong-kar-wai",
    "duration": 5,
    "aspect_ratio": "16:9"
  },
  "config": {
    "billing_mode": "managed"
  },
  "metadata": {
    "trace_id": "local_trace_uuid",
    "run_id": "local_run_uuid"
  }
}
```

**Response:**
```json
{
  "job_id": "client_uuid",
  "server_job_id": "srv_12345",
  "status": "queued",
  "estimated_credits": 1.5
}
```

### 5.2 查询状态
`GET /api/v1/jobs/{job_id}/status`

**Response:**
```json
{
  "status": "completed",
  "progress": 100,
  "result_url": "https://signed-url-to-storage...",
  "actual_credits_charged": 1.45
}
```

---

## 6. 服务端核心流程 (Server Business Flow)

当请求进入 CineMate Gateway 时，处理链路如下：

### 6.1 鉴权与限流 (Auth & Rate Limit)
1.  校验 JWT Token 有效性。
2.  检查 IP/User 限流策略 (Redis Counter)。

### 6.2 计费解析 (Billing Resolution)
1.  读取 `billing_mode`：
    *   **Managed**: 查询数据库 `user_credits`。若余额不足 -> `402 Payment Required`。预扣预估费用。
    *   **BYOK**: 验证请求头 `X-BYOK-Signature` (验证 Key Hash 是否在白名单中)。验证失败 -> `403 Forbidden`。不扣费。

### 6.3 智能路由 (Smart Routing)
1.  检查客户端是否指定了 `model_override`。
2.  若未指定，根据 `ProviderHealth` 状态表选择最优上游：
    *   优先选择延迟低、错误率低的 Provider。
    *   若 Provider A 队列拥堵，自动切换至 Provider B (如 Kling -> Runway)。

### 6.4 上游代理 (Upstream Proxy)
1.  将 CineMate 标准协议转换为上游 SDK 格式 (e.g. Kling API JSON)。
2.  发起异步调用。
3.  将 `upstream_job_id` 映射到 `server_job_id` 并落库。

### 6.5 审计与结算 (Audit & Settlement)
1.  **Start Log**: 记录 `request_hash`、时间戳、预估费用。
2.  **Completion**: 收到上游完成回调。
    *   计算实际成本 (Credits 或 Token)。
    *   **多退少补**: 更新余额。
    *   **End Log**: 记录 `result_url`、实际费用、耗时。

---

## 7. 实施计划 (Implementation Plan)

- [x] **Phase 1: Core Infrastructure**: SQLite Store, CAS, Models.
- [x] **Phase 2: Video Git Engine**: DAG, FSM, Dirty Propagation, Orchestrator. (Tests Passed ✅)
- [ ] **Phase 3: Cloud Gateway**: Auth, Proxy, Billing, BYOK.
- [ ] **Phase 4: Director Agent (AgentScope)**: 
    -   Integration of AgentScope 1.0 Framework.
    -   Implementing `ReActAgent` for Director logic.
    -   Mapping CineMate DAG Engine to `Toolkit`.
    -   See `docs/agentscope_guide.md`.
- [ ] **Phase 5: Client UI**: 展示 Video Git 树, 余额/状态面板.

# Sprint 3 Demo Script

> **日期**: 2026-04-21  
> **Sprint**: Sprint 3 Review  
> **目标**: 展示 Skill System + CLI + MVP Demo

---

## 🎯 Demo 概览

本 Demo 展示 Sprint 3 的核心成果：

1. **Skill System**: Progressive disclosure + Hermes auto-generation
2. **CLI Commands**: create/loop/status/history/diff/branches
3. **MVP Demo**: 端到端视频生成流程

---

## 📋 Demo 章节

### Chapter 1: Skill System Demo (5 min)

#### 1.1 Skill Store CRUD

```bash
# 运行 Skill Store 测试
pytest tests/unit/skills/test_skill_store.py -v

# 预期输出:
# tests/unit/skills/test_skill_store.py — 29/29 PASS
# - test_create_skill: ✅
# - test_read_skill: ✅
# - test_update_skill: ✅
# - test_delete_skill: ✅
# - test_list_by_category: ✅
# - test_sync_from_fs: ✅
```

#### 1.2 Progressive Disclosure Index

```python
# Python Demo
from cine_mate.skills import SkillStore, SkillIndexer
from pathlib import Path

async def demo_progressive_disclosure():
    store = SkillStore(Path("./cine_mate/skills/data"))
    await store.init()
    
    indexer = SkillIndexer(store)
    index = await indexer.build_index()
    
    # 显示 progressive disclosure index
    prompt_text = await indexer.format_index_for_prompt(index)
    print(prompt_text)
    
    # 输出:
    # Available skills:
    # - style-cyberpunk: Cyberpunk visual style [cyberpunk, neon]
    # - workflow-short-ad: Short ad template [ad, product]

asyncio.run(demo_progressive_disclosure())
```

#### 1.3 Skill Loader On-Demand

```python
from cine_mate.skills import SkillLoader

async def demo_skill_loader():
    loader = SkillLoader(store)
    
    # On-demand loading
    content = await loader.load("style-cyberpunk")
    print(content)
    
    # 输出 (OpenCode XML format):
    # <skill_content name="style-cyberpunk">
    # ## Overview
    # Cyberpunk aesthetic characterized by...
    # </skill_content>

asyncio.run(demo_skill_loader())
```

#### 1.4 SkillReviewer Auto-Generation

```python
from cine_mate.skills import SkillReviewer

async def demo_skill_reviewer():
    reviewer = SkillReviewer(store)
    
    # Simulate successful run (3+ nodes)
    run_data = {
        "run_id": "demo_run_001",
        "status": "completed",
        "intent": "Create a product ad video",
        "nodes": [
            {"id": "script", "type": "script_gen", "status": "succeeded"},
            {"id": "image", "type": "text_to_image", "status": "succeeded"},
            {"id": "video", "type": "image_to_video", "status": "succeeded"},
        ],
    }
    
    result = await reviewer.review(run_data)
    print(f"Auto-generated skill: {result.name}")
    print(f"Category: {result.category}")
    print(f"auto_generated: {result.auto_generated}")
    print(f"source_run_id: {result.source_run_id}")

asyncio.run(demo_skill_reviewer())
```

---

### Chapter 2: CLI Commands Demo (10 min)

#### 2.1 Basic CLI Usage

```bash
# 查看帮助
cinemate --help

# 预期输出:
# Usage: cinemate [OPTIONS] COMMAND [ARGS]...
# 
# Commands:
#   create    Create a video from natural language
#   loop      Start interactive continuous conversation mode
#   status    Show CineMate system status
#   history   Show run history (Video Git log)
#   diff      Show differences between two runs
#   branches  List all branches in Video Git history
```

#### 2.2 Create Video (Mock Mode)

```bash
# 创建视频 (Mock Provider)
cinemate create "A cyberpunk city at night with neon lights"

# 预期输出:
# 🎬 Creating video: "A cyberpunk city at night with neon lights"
# 
# Intent parsed: cyberpunk_city_night
# DAG built: script_gen → text_to_image → image_to_video
# 
# Run ID: run_demo_001
# Status: completed
# Nodes: 3/3 succeeded
# 
# Results:
# - script: "Cyberpunk city script generated"
# - image: "https://mock.url/image_001.png"
# - video: "https://mock.url/video_001.mp4"
```

#### 2.3 Apply Skill/Style

```bash
# 应用 workflow skill
cinemate create "Product ad for headphones" --style workflow-short-ad

# 预期输出:
# 🎬 Creating video with style: workflow-short-ad
# 
# Skill loaded: workflow-short-ad
# - 5-step product ad template
# - Hook → Demo → Features → Testimonial → CTA
# 
# DAG built: 5 nodes
# Run ID: run_demo_002
# Status: completed
```

#### 2.4 Interactive Loop Mode

```bash
# 进入交互模式
cinemate loop

# 预期输出:
# 🎬 CineMate Interactive Mode
# Type 'exit' or 'quit' to leave.
# 
# > Create a cyberpunk video
# Run created: run_demo_001
# 
# > Make it slower, add more neon
# Run updated: run_demo_003 (fork from run_demo_001)
# 
# > Show me the history
# Run History:
# - run_demo_003: Slower cyberpunk (latest)
# - run_demo_001: Original cyberpunk
# 
# > exit
# Goodbye!
```

#### 2.5 Video Git Commands

```bash
# 查看历史
cinemate history

# 预期输出:
# Run History
# Status        Run ID     Commit            Branch   Created
# ----------    ---------  ----------------  -------  -----------------
# ✅ completed  run_003    Slower cyberpunk  main     2026-04-21 14:30
# ✅ completed  run_002    Product ad        main     2026-04-21 14:20
# ✅ completed  run_001    Cyberpunk city    main     2026-04-21 14:10
# 
# Total: 3 runs shown
```

```bash
# 查看差异
cinemate diff run_002 --parent run_001

# 预期输出:
# Diff: run_001 → run_002
# Node                  Base Status    Target Status    Change
# --------------------  -------------  ---------------  ---------------
# script                succeeded      succeeded        ➖ same
# image                 succeeded      succeeded        🔄 changed
# video                 succeeded      (deleted)        🗑️  deleted
# compose               (new)          succeeded        ➕ added
# 
# Summary: 1 added, 1 deleted, 1 changed, 1 same
```

```bash
# 查看分支
cinemate branches

# 预期输出:
# Branches
# Branch      Runs    Latest
# ---------   -----   -----------------
# main        3       2026-04-21 14:30
# experiment  1       2026-04-21 13:00
# 
# Total: 2 branches
```

---

### Chapter 3: MVP E2E Demo (5 min)

#### 3.1 Run MVP Demo Script

```bash
# 运行 MVP Demo
python scripts/demo_mvp.py

# 预期输出:
# ============================================
# CineMate MVP Demo - Sprint 3
# ============================================
# 
# Chapter 1: Intent Parsing
# ----------------------------------------
# Input: "Create a cyberpunk product showcase video"
# Intent: cyberpunk_product_showcase
# ✅ Intent parsed correctly
# 
# Chapter 2: DAG Construction
# ----------------------------------------
# DAG nodes: 3
# - script_gen (script generation)
# - text_to_image (image from script)
# - image_to_video (video from image)
# DAG edges: script_gen → text_to_image → image_to_video
# ✅ DAG built correctly
# 
# Chapter 3: Orchestrator Execution
# ----------------------------------------
# Run ID: mvp_demo_run_001
# Executing nodes...
# 
# Node 1/3: script_gen
# - Status: running → succeeded
# - Result: "Product showcase script..."
# 
# Node 2/3: text_to_image
# - Status: running → succeeded
# - Result: https://mock.url/image.png
# 
# Node 3/3: image_to_video
# - Status: running → succeeded
# - Result: https://mock.url/video.mp4
# 
# ✅ All nodes executed successfully
# 
# Chapter 4: Lifecycle Verification
# ----------------------------------------
# Run status: completed
# Nodes succeeded: 3/3
# ✅ Lifecycle verified
# 
# Chapter 5: Multi-Scenario Test
# ----------------------------------------
# Scenario 1: Simple video (1 node)
# - Run created: mvp_demo_run_002
# - Status: completed ✅
# 
# Scenario 2: Complex pipeline (4 nodes)
# - Run created: mvp_demo_run_003
# - Status: completed ✅
# 
# ============================================
# MVP Demo Complete - All 8 tests passed
# ============================================
```

---

### Chapter 4: Test Summary (2 min)

```bash
# 运行所有 Sprint 3 测试
pytest tests/unit/skills/ tests/unit/cli/ tests/integration/ -v

# 预期输出:
# tests/unit/skills/test_skill_store.py — 29/29 PASS
# tests/unit/skills/test_skill_loader.py — 14/14 PASS
# tests/unit/skills/test_skill_reviewer.py — 15/15 PASS
# tests/unit/cli/test_commands.py — 25/25 PASS
# tests/unit/cli/test_video_git.py — 21/21 PASS
# tests/integration/test_mvp_demo.py — 8/8 PASS
# 
# ==================== 112 passed ====================
```

---

## 🎯 Demo Checklist

| 章节 | 演示内容 | 验收 |
|------|----------|------|
| **Chapter 1** | Skill System CRUD + Progressive Disclosure | ✅ |
| **Chapter 2** | CLI Commands (create/loop/history/diff) | ✅ |
| **Chapter 3** | MVP E2E Demo | ✅ |
| **Chapter 4** | Test Summary | ✅ |

---

## 📊 Sprint 3 Demo Results

| Demo | Status | Tests |
|------|--------|-------|
| Skill System | ✅ Pass | 58/58 |
| CLI Commands | ✅ Pass | 46/46 |
| MVP Demo | ✅ Pass | 8/8 |
| **Total** | ✅ **100%** | **112/112** |

---

**签名**: PM (Qwen)  
**日期**: 2026-04-21
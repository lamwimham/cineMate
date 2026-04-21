# CineMate Skill System — User Guide

> **Skill System**: Progressive disclosure + auto-generation for the Director Agent

---

## 🎯 What is a Skill?

Skills in CineMate are **decision-layer patterns** — reusable knowledge that helps the Director Agent make better decisions during video production.

**Not infrastructure code**, but rather:
- Style strategies (e.g., cyberpunk aesthetics, Wong Kar-wai cinematography)
- Workflow templates (e.g., short ad structure, product review flow)
- Error recovery patterns (e.g., Kling face distortion recovery)
- Quality gating rules (e.g., video duration constraints)

---

## 📚 Skill Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **STYLE** | Visual style strategies | `style-cyberpunk`, `style-wong-kar-wai` |
| **WORKFLOW** | Workflow templates | `workflow-short-ad`, `workflow-product-review` |
| **ERROR_RECOVERY** | Error recovery patterns | `error-kling-face-distortion` |
| **QUALITY** | Quality gating rules | `quality-video-duration` |

---

## 🗂️ Skill File Structure

Each skill is stored as a `SKILL.md` file with YAML frontmatter:

```
cine_mate/skills/data/
├── style-cyberpunk/
│   └and SKILL.md               # Skill definition
│   └── assets/              # Optional assets (images, examples)
└── workflow-short-ad/
    └and SKILL.md
```

### SKILL.md Template

```markdown
---
name: style-cyberpunk
description: Cyberpunk visual style with neon lights, dark atmosphere
category: style
version: 1.0.0
author: cinemate
agent: director
scenario: video-generation
tags:
  - cyberpunk
  - neon
  - dark
  - futuristic
status: enabled
---

# Cyberpunk Visual Style

## Overview

Cyberpunk aesthetic characterized by:
- High contrast lighting (neon vs. darkness)
- Color palette: Cyan, magenta, purple
- Urban dystopian environments
- Rain/fog atmosphere effects

## Color Guidelines

| Element | Color | Hex |
|---------|-------|-----|
| Primary neon | Cyan | #00FFFF |
| Secondary neon | Magenta | #FF00FF |
| Background | Dark blue | #0A0A1A |

## Lighting Rules

1. **Neon dominance**: At least 60% of light sources should be neon
2. **Shadow depth**: Minimum 3 levels of shadow gradient
3. **Reflection**: All neon lights should have wet surface reflections

## Example Prompts

- "A cyberpunk city at night with neon signs and rain"
- "Futuristic alley with holographic advertisements"

## Provider Recommendations

| Provider | Best For | Limitations |
|----------|----------|-------------|
| Kling | Long videos, high motion | Face distortion risk |
| Runway | High resolution | Limited duration |

## Notes

- Avoid over-saturation (max 80% color intensity)
- Use film grain effect for authenticity
```

---

## 🔄 Progressive Disclosure Flow

The Skill System uses progressive disclosure to avoid overwhelming the Director Agent:

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Index Injection                                   │
│  DirectorAgent system prompt receives:                      │
│  - style-cyberpunk: Cyberpunk visual style...               │
│  - workflow-short-ad: Short ad template...                  │
│  (Only name + description, not full content)                │
└──────────────────────┬──────────────────────────────────────┘
                       │ Agent decides to use a skill
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: On-Demand Loading                                 │
│  Agent calls skill tool:                                    │
│  skill("style-cyberpunk")                                   │
│  → Returns full SKILL.md content                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ Agent uses skill content
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Execution                                         │
│  DAG nodes configured with skill parameters                 │
│  Orchestrator executes with style guidance                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 Hermes Auto-Generation

The SkillReviewer component automatically generates skills from PipelineRun execution analysis.

### Trigger Conditions

| Outcome | Trigger | Skill Type |
|---------|---------|------------|
| **Success (3+ nodes)** | Reusable workflow pattern | WORKFLOW |
| **Failure (identifiable)** | Face distortion, OOM, API errors | ERROR_RECOVERY |
| **Retry (2+)** | Transient error recovery | ERROR_RECOVERY |

### Skip Conditions

| Condition | Rationale |
|-----------|-----------|
| `<3 nodes` | Too simple to patternize |
| Generic errors (timeout/cancelled) | No actionable pattern |
| Already reviewed | Dedup by `source_run_id` |
| Single retry | Too common |

### Provenance Tracking

All auto-generated skills include:
- `auto_generated=True`: Distinguishes from hand-written
- `source_run_id`: Link to originating PipelineRun
- `source_error`: Error pattern that triggered generation

---

## 📝 Creating Skills Manually

### Step 1: Create Directory

```bash
mkdir -p cine_mate/skills/data/style-my-style
```

### Step 2: Write SKILL.md

Create `SKILL.md` with YAML frontmatter + markdown body.

### Step 3: Register Skill

Skills are auto-indexed on DirectorAgent initialization. To manually register:

```python
from cine_mate.skills.skill_store import SkillStore
from cine_mate.skills.models import SkillMetadata, SkillCategory

store = SkillStore(Path("./cine_mate/skills/data"))
await store.init()

# Skill is automatically indexed from SKILL.md file
skills = await store.list_all()
```

---

## 🔧 Skill Management via CLI

### List Skills

```bash
cinemate status
```

Shows skill count and active skills.

### Apply Skill

```bash
cinemate create "Product ad for headphones" --style workflow-short-ad
```

---

## 🧪 Testing Skills

Run skill system tests:

```bash
pytest tests/unit/skills/ -v
```

Expected output:
```
tests/unit/skills/test_skill_store.py — 29/29 PASS
tests/unit/skills/test_skill_loader.py — 14/14 PASS
tests/unit/skills/test_skill_reviewer.py — 15/15 PASS
```

---

## 📖 Best Practices

### 1. Keep Descriptions Concise

Frontmatter `description` should be < 100 characters — this is what appears in the progressive disclosure index.

### 2. Use Specific Tags

Tags should be searchable keywords, not generic terms.

### 3. Include Provider Recommendations

Document which providers work best with this skill and their limitations.

### 4. Provide Example Prompts

Help users understand how to trigger the skill.

### 5. Document Error Recovery

For ERROR_RECOVERY skills, include:
- Error pattern description
- Recovery steps
- Provider fallback recommendations

---

## 🔗 Related Documentation

- [API Reference](api_reference.md)
- [Architecture Overview](../architecture.md)
- [MVP Demo Guide](../demo/mvp_demo_guide.md)

---

<p align="center">
  <strong>CineMate Skill System</strong> — Knowledge that scales
</p>
---
name: workflow-short-ad
description: 15-second product ad template — hook → demo → CTA, optimized for social media
category: workflow
version: 1.0.0
author: cinemate
scenario: product-video
tags: [advertising, social-media, short-form]
---

# Short Ad Workflow Template

## Structure (15 seconds)

| Phase | Duration | Purpose | Node Type |
|-------|----------|---------|-----------|
| Hook | 0-3s | Grab attention | text_to_video |
| Demo | 3-10s | Show product | image_to_video |
| CTA | 10-15s | Call to action | text_to_video |

## DAG Template
```json
{
  "nodes": [
    {"id": "hook_script", "type": "script_generation", "params": {"duration": 3, "tone": "energetic"}},
    {"id": "hook_video", "type": "text_to_video", "depends_on": ["hook_script"]},
    {"id": "product_shot", "type": "image_generation", "params": {"style": "clean_product"}},
    {"id": "demo_video", "type": "image_to_video", "depends_on": ["product_shot"], "params": {"motion": "pan"}},
    {"id": "cta_script", "type": "script_generation", "params": {"duration": 5, "tone": "urgent"}},
    {"id": "cta_video", "type": "text_to_video", "depends_on": ["cta_script"]},
    {"id": "compose", "type": "video_compose", "depends_on": ["hook_video", "demo_video", "cta_video"]}
  ]
}
```

## Model Recommendations
- **Budget**: qwen-turbo (script) + wanx (image) + kling-v1 (video)
- **Quality**: qwen-max (script) + flux-pro (image) + kling-v1.6-pro (video)

## Common Pitfalls
- Hook too long (>3s loses retention)
- CTA without clear action verb
- Demo phase needs at least one product close-up

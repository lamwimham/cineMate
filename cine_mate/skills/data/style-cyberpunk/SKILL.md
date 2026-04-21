---
name: style-cyberpunk
description: Cyberpunk visual style — neon lights, rain-soaked streets, high contrast, synthwave color palette
category: style
version: 1.0.0
author: cinemate
scenario: style-transfer
tags: [neon, dark, sci-fi, synthwave]
---

# Cyberpunk Style Guide

## Visual Characteristics
- **Color palette**: Cyan (#00FFFF), magenta (#FF00FF), deep blue (#0A0A2E), neon pink
- **Lighting**: High contrast, volumetric fog, lens flares, neon glow
- **Environment**: Rain-soaked streets, holographic billboards, dense urban architecture
- **Mood**: Dystopian, high-tech low-life, atmospheric

## Prompt Template
```
{subject}, cyberpunk style, neon lights, rain, dark city background,
cyan and magenta lighting, volumetric fog, cinematic, 4k, --ar 16:9
```

## Model-Specific Tips
- **Kling I2V**: Add "slow camera pan" for best motion results
- **Flux T2I**: Use `--v 2` for enhanced neon rendering
- **Runway Gen-3**: Set motion bucket to 7 for subtle atmospheric movement

## Avoid
- Over-exposed scenes (neon should glow, not bleach)
- Generic "futuristic" without specific cyberpunk markers
- Daylight scenes (cyberpunk is primarily nocturnal)

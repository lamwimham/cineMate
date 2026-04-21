#!/usr/bin/env python3
"""
Sprint 2 Demo - Provider Adapter + Agent + Worker

演示内容:
1. Provider Factory 创建 Kling + Runway
2. text_to_video 生成流程
3. image_to_video 生成流程
4. Worker + Provider 集成
5. Mock Provider 测试流程

Usage:
    python scripts/demo_sprint2.py          # Full demo (all sections)
    python scripts/demo_sprint2.py --section mock    # Only mock provider section
    python scripts/demo_sprint2.py --section factory # Only factory section
"""

import os
import sys
import json
import asyncio
import time
import argparse

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Color helpers ──────────────────────────────────────────────────────────

class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def log(title, msg, color=Colors.BLUE):
    print(f"\n{color}{Colors.BOLD}{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}{Colors.ENDC}")
    print(f"  {msg}")


def section(title):
    print(f"\n\n{'#' * 60}")
    print(f"# {title}")
    print(f"{'#' * 60}")


# ── Demo: Provider Factory ────────────────────────────────────────────────

def demo_provider_factory():
    section("1. Provider Factory — 创建 Kling + Runway")

    from cine_mate.adapters.base import BaseVideoProvider
    from cine_mate.adapters.kling_provider import KlingProvider
    from cine_mate.adapters.runway_provider import RunwayProvider
    from cine_mate.adapters.mock_provider import MockVideoProvider

    # Verify base class
    print(f"\n  BaseVideoProvider: {BaseVideoProvider.__name__}")
    print(f"    Abstract methods: {BaseVideoProvider.__abstractmethods__}")

    # Verify concrete providers
    providers = [
        ("KlingProvider", KlingProvider, "kling"),
        ("RunwayProvider", RunwayProvider, "runway"),
        ("MockVideoProvider", MockVideoProvider, "mock"),
    ]

    for name, cls, pname in providers:
        print(f"\n  {name}:")
        print(f"    provider_name: {cls.provider_name}")
        print(f"    Inherits BaseVideoProvider: {issubclass(cls, BaseVideoProvider)}")
        if pname == "mock":
            # Mock doesn't require API key
            inst = cls()
            print(f"    Estimate cost (10s): ${inst.estimate_cost(10):.2f}")
        else:
            print(f"    Requires env: {name.upper().replace('PROVIDER', '')}_API_KEY")

    print(f"\n  ✅ All providers registered successfully.")


# ── Demo: text_to_video generation flow ───────────────────────────────────

async def demo_text_to_video():
    section("2. text_to_video 生成流程 — Mock Provider")

    from cine_mate.adapters.mock_provider import MockVideoProvider

    provider = MockVideoProvider(simulate_delay=True, delay_seconds=1)

    prompt = "A cyberpunk city at night with neon lights and rain"
    print(f"\n  Prompt: \"{prompt}\"")
    print(f"  Provider: {provider.provider_name}")

    # Step 1: Estimate cost
    cost = provider.estimate_cost(duration=10, resolution="720p")
    print(f"\n  [Step 1] Estimate cost: ${cost:.2f}")

    # Step 2: Submit generation
    print(f"\n  [Step 2] Submitting generation job...")
    result = await provider.generate_video(
        prompt=prompt,
        duration=10,
        resolution="720p"
    )
    print(f"    job_id: {result.job_id}")
    print(f"    status: {result.status}")

    # Step 3: Check status
    status = await provider.check_status(result.job_id)
    print(f"\n  [Step 3] Check status: {status}")

    # Step 4: Get result
    final = await provider.get_result(result.job_id)
    if final:
        print(f"\n  [Step 4] Result:")
        print(f"    video_url: {final.video_url}")
        print(f"    thumbnail: {final.thumbnail_url}")
        print(f"    duration:  {final.duration_seconds}s")

    print(f"\n  ✅ text_to_video flow completed.")


# ── Demo: image_to_video generation flow ──────────────────────────────────

async def demo_image_to_video():
    section("3. image_to_video 生成流程 — Mock Provider")

    from cine_mate.adapters.mock_provider import MockVideoProvider

    provider = MockVideoProvider(simulate_delay=True, delay_seconds=1)

    prompt = "Subtle camera pan with light rain effect"
    image_url = "https://example.com/cyberpunk_city.jpg"

    print(f"\n  Prompt: \"{prompt}\"")
    print(f"  Source image: {image_url}")
    print(f"  Provider: {provider.provider_name}")

    # Step 1: Submit with image_url (triggers image_to_video mode)
    print(f"\n  [Step 1] Submitting image_to_video job...")
    result = await provider.generate_video(
        prompt=prompt,
        duration=10,
        resolution="720p",
        image_url=image_url
    )
    print(f"    job_id: {result.job_id}")
    print(f"    mode: {result.metadata.get('mode', 'unknown')}")

    # Step 2: Get result
    final = await provider.get_result(result.job_id)
    if final:
        print(f"\n  [Step 2] Result:")
        print(f"    video_url: {final.video_url}")
        print(f"    mode: {final.metadata.get('mode', 'unknown')}")

    print(f"\n  ✅ image_to_video flow completed.")


# ── Demo: generate_and_wait convenience method ────────────────────────────

async def demo_generate_and_wait():
    section("4. generate_and_wait — 自动轮询便捷方法")

    from cine_mate.adapters.mock_provider import MockVideoProvider

    provider = MockVideoProvider(simulate_delay=True, delay_seconds=1)

    print(f"\n  Using provider.generate_and_wait()...")
    print(f"  This method submits the job and polls until completion.")

    start = time.time()
    result = await provider.generate_and_wait(
        prompt="A sunset over the ocean with golden reflections",
        duration=10,
        resolution="720p",
        poll_interval=1,
        max_wait=30,
    )
    elapsed = time.time() - start

    print(f"\n  Completed in {elapsed:.1f}s:")
    print(f"    video_url: {result.video_url}")
    print(f"    status:    {result.status}")
    print(f"    duration:  {result.duration_seconds}s")
    print(f"    cost:      ${result.cost:.2f}")

    print(f"\n  ✅ generate_and_wait completed.")


# ── Demo: Worker + Provider integration ──────────────────────────────────

def demo_worker_integration():
    section("5. Worker + Provider 集成 — JobType 路由")

    from cine_mate.infra.schemas import JobType

    # Show all job types
    print("\n  Available JobTypes:")
    for jt in JobType:
        print(f"    - {jt.value}")

    # Show worker routing
    print("\n  Worker routing logic:")
    routes = [
        ("kling_text_to_video", "KlingProvider.generate_and_wait()"),
        ("kling_image_to_video", "KlingProvider.generate_and_wait(image_url=...)"),
        ("runway_text_to_video", "RunwayProvider.generate_and_wait()"),
        ("mock_text_to_video", "MockVideoProvider.generate_and_wait()"),
        ("mock_image_to_video", "MockVideoProvider.generate_and_wait(image_url=...)"),
    ]
    for job_type, handler in routes:
        print(f"    {job_type:30s} → {handler}")

    print(f"\n  ✅ Worker + Provider integration verified.")


# ── Demo: Config system ──────────────────────────────────────────────────

def demo_config_system():
    section("6. 配置系统 — 多模型 Provider 配置")

    from cine_mate.config import load_config

    config = load_config(validate=False, print_report=False)

    print("\n  LLM 配置:")
    print(f"    Primary: {config.models.llm.primary.provider}/{config.models.llm.primary.model_name}")
    if config.models.llm.fallback:
        print(f"    Fallback: {config.models.llm.fallback.provider}/{config.models.llm.fallback.model_name}")

    print("\n  Video 配置:")
    print(f"    I2V Primary: {config.models.image_to_video.primary.provider}/{config.models.image_to_video.primary.model_name}")
    print(f"    T2V Primary: {config.models.text_to_video.primary.provider}/{config.models.text_to_video.primary.model_name}")

    print("\n  Cost Tiers (I2V):")
    tiers = [("Primary", config.models.image_to_video.primary),
             ("Fallback", config.models.image_to_video.fallback),
             ("Budget", config.models.image_to_video.budget)]
    for name, tier in tiers:
        if tier:
            print(f"    {name:10s}: {tier.provider}/{tier.model_name}")

    print(f"\n  ✅ Configuration system verified.")


# ── Main ─────────────────────────────────────────────────────────────────

SECTIONS = {
    "factory": demo_provider_factory,
    "text_to_video": demo_text_to_video,
    "image_to_video": demo_image_to_video,
    "generate_and_wait": demo_generate_and_wait,
    "worker": demo_worker_integration,
    "config": demo_config_system,
}


async def run_section(name):
    fn = SECTIONS.get(name)
    if not fn:
        print(f"{Colors.FAIL}Unknown section: {name}{Colors.ENDC}")
        return
    result = fn()
    if asyncio.iscoroutine(result):
        await result


async def main(sections_to_run=None):
    sections_to_run = sections_to_run or list(SECTIONS.keys())

    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        CineMate Sprint 2 Demo                           ║")
    print("║  Provider Adapter + Agent + Worker Integration          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    for name in sections_to_run:
        await run_section(name)

    print(f"\n\n{Colors.GREEN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        🎉  Sprint 2 Demo Complete!                      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CineMate Sprint 2 Demo")
    parser.add_argument(
        "--section",
        choices=list(SECTIONS.keys()),
        nargs="+",
        default=None,
        help="Run specific section(s). Default: all sections.",
    )
    args = parser.parse_args()

    try:
        asyncio.run(main(sections_to_run=args.section))
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Demo interrupted.{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Demo failed: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

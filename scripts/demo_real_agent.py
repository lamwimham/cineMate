"""
CineMate Day 2 Demo: Real Agent Call with DashScope API

Usage:
    python scripts/demo_real_agent.py          # Real API (requires DASHSCOPE_API_KEY)
    python scripts/demo_real_agent.py --mock   # Mock mode (no API key needed)

Demo Flow:
    1. [INIT] Load config, validate API keys
    2. [AGENT] Create DirectorAgent with real/mock model
    3. [TOOL] Register EngineTools with JobQueue
    4. [EXEC] Send natural language prompt, receive DAG plan
"""

import asyncio
import json
import os
import sys
import argparse

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from cine_mate.config import load_config
from cine_mate.agents.director_agent import DirectorAgent
from cine_mate.agents.tools.engine_tools import EngineTools
from cine_mate.infra.queue import JobQueue
from cine_mate.infra.event_bus import EventBus

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(step, msg, color=Colors.BLUE):
    print(f"\n{color}{Colors.BOLD}{'='*40}\n[{step}]\n{'='*40}{Colors.ENDC}")
    print(f"  {msg}")


async def demo(use_mock=False):
    log("INIT", f"🎬 CineMate Day 2 Demo (Mode: {'Mock' if use_mock else 'Real'})", Colors.HEADER)

    # 1. Load config (validates API keys)
    log("CONFIG", "📦 Loading configuration...")
    if use_mock:
        config = load_config(validate=False, print_report=False)
        print("  ⏭️  Skipping API key validation (mock mode)")
    else:
        config = load_config(validate=True, print_report=True)

    # 2. Setup infrastructure
    log("INFRA", "🔧 Initializing infrastructure...")
    event_bus = EventBus(config.infra.redis_url)
    await event_bus.connect()
    
    queue = JobQueue(config.infra.redis_url, event_bus=event_bus)
    await queue.connect()
    print("  ✅ EventBus and JobQueue connected")

    # 3. Setup EngineTools
    tools = EngineTools(
        store_path=config.infra.db_path,
        job_queue=queue
    )
    await tools.init_db()
    print("  ✅ EngineTools initialized")

    # 4. Create DirectorAgent
    log("AGENT", "🤖 Creating DirectorAgent...")
    if use_mock:
        print("  Using MockChatModel (no API call)")
    else:
        print(f"  Using DashScope API (model: qwen-max)")
    
    agent = DirectorAgent(
        name="Director",
        model_name="qwen-max",
        engine_tools=tools,
        use_mock=use_mock,
    )
    print("  ✅ DirectorAgent created")

    # 5. Send prompt
    log("EXEC", "💬 Sending prompt to Agent...")
    prompt = "Create a 10-second cyberpunk city scene at night with neon lights"
    print(f'  User: "{prompt}"')
    
    try:
        # Call the agent - it will parse the intent and generate a DAG plan
        # The Agent's ReAct loop will use tools to create the pipeline
        from agentscope.message import Msg
        user_msg = Msg(name="user", content=prompt, role="user")
        result = await agent.reply(user_msg)
        print(f"\n  {Colors.GREEN}✅ Agent Response:{Colors.ENDC}")
        print(f"  {result.content if hasattr(result, 'content') else result}")
    except Exception as e:
        print(f"\n  {Colors.FAIL}❌ Agent call failed: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
    finally:
        await event_bus.disconnect()
        await queue.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Use mock mode (no API key)")
    args = parser.parse_args()
    
    try:
        asyncio.run(demo(use_mock=args.mock))
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Demo interrupted.{Colors.ENDC}")
    except ValueError as e:
        print(f"{Colors.FAIL}Configuration error: {e}{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}Demo failed: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()

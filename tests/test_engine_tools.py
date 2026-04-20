"""
Test Script for Engine Tools Integration
"""

import asyncio
import sys
import os

sys.path.append(os.getcwd())

from agentscope.tool import Toolkit
from agentscope.message import Msg
from cine_mate.agents.tools.engine_tools import register_engine_tools

async def test_tools():
    print("Initializing Engine Tools...")
    
    toolkit = Toolkit()
    manager = register_engine_tools(toolkit)
    await manager.init_db()
    
    # 1. Test Create Video
    print("\n--- Testing create_video ---")
    try:
        # Manually invoke to check structure
        response = await manager.create_video("A cyberpunk city", style="wong-kar-wai")
        content = response.content[0]
        print(f"Response Type: {content['type']}")
        print(f"Response Text: {content['text']}")
        
        # Parse result
        import json
        data = json.loads(content['text'])
        run_id = data['run_id']
        print(f"Extracted Run ID: {run_id}")
        
        # 2. Test Get Status
        print("\n--- Testing get_run_status ---")
        status_resp = await manager.get_run_status(run_id)
        print(f"Status Response: {status_resp.content[0]['text']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_tools())

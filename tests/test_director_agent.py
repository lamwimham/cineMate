"""
Test Script for DirectorAgent (Task 2.3)
Tests Agent initialization, Prompt loading, and Tool integration.
"""

import asyncio
import sys
import os
import json

sys.path.append(os.getcwd())

from cine_mate.agents.director_agent import load_system_prompt
from cine_mate.agents.tools.engine_tools import EngineTools
from agentscope.tool import Toolkit

async def test_prompt_loading():
    print("Testing prompt loading...")
    prompt = load_system_prompt()
    assert "You are CineMate's Director Agent" in prompt
    assert "text_to_image" in prompt
    assert "image_to_video" in prompt
    assert "Wong Kar-wai" in prompt
    print("✅ Prompt loaded correctly and contains expected content.")

async def test_tool_integration():
    print("\nTesting Tool integration...")
    
    manager = EngineTools()
    await manager.init_db()
    
    toolkit = Toolkit()
    toolkit.register_tool_function(manager.create_video)
    toolkit.register_tool_function(manager.submit_plan)
    
    # 1. Test submit_plan with valid JSON
    dag = {
        "intent": "Test DAG",
        "nodes": [
            {"id": "node_1", "type": "text_to_image", "params": {"prompt": "test"}},
            {"id": "node_2", "type": "image_to_video", "inputs": ["node_1"]}
        ],
        "output_node": "node_2"
    }
    
    resp = await manager.submit_plan(json.dumps(dag))
    result_text = resp.content[0]["text"]
    result = json.loads(result_text)
    
    assert result["status"] == "accepted"
    assert result["node_count"] == 2
    print(f"✅ submit_plan accepted DAG. Run ID: {result['run_id']}")
    
    # 2. Test submit_plan with invalid JSON
    resp_err = await manager.submit_plan("{bad json")
    err_text = resp_err.content[0]["text"]
    assert "Invalid JSON" in err_text
    print("✅ submit_plan rejected invalid JSON.")

if __name__ == "__main__":
    asyncio.run(test_prompt_loading())
    asyncio.run(test_tool_integration())

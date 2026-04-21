"""
Integration Test: Multi-Node DAG Submission
Verifies if JobQueue processes jobs sequentially or in parallel when submitted immediately.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from cine_mate.infra import JobQueue
from cine_mate.infra.schemas import JobType

async def test_multi_node_dag():
    # 1. Connect
    queue = JobQueue(redis_url="redis://localhost:6379")
    try:
        await queue.connect()
        print("✅ Connected to JobQueue (Redis)")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return

    try:
        # 2. Define 3-Node DAG (Script -> Image -> Video)
        # We submit them sequentially to simulate Engine logic 
        
        print("\n--- SUBMITTING NODE 1 (Image - Script is skipped in this test) ---")
        job_1_id = await queue.submit_job(
            run_id="test_dag_001",
            node_id="node_img_gen",
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": "Write a cyberpunk script"}
        )
        print(f"✅ Job 1 Submitted: {job_1_id}")

        # Submit Node 2 & 3 IMMEDIATELY to test "All at Once" behavior
        print("\n--- SUBMITTING NODE 2 (Image) & NODE 3 (Video) IMMEDIATELY ---")
        
        job_2_id = await queue.submit_job(
            run_id="test_dag_001",
            node_id="node_img_gen",
            job_type=JobType.TEXT_TO_IMAGE,
            params={"prompt": "Cyberpunk city"}
        )
        
        job_3_id = await queue.submit_job(
            run_id="test_dag_001",
            node_id="node_vid_gen",
            job_type=JobType.IMAGE_TO_VIDEO,
            params={"prompt": "Animate city"}
        )

        print(f"✅ Job 2 Submitted: {job_2_id}")
        print(f"✅ Job 3 Submitted: {job_3_id}")

        # 3. IMMEDIATE STATUS CHECK
        print("\n--- IMMEDIATE STATUS CHECK ---")
        status_1 = await queue.get_job_status(job_1_id)
        status_2 = await queue.get_job_status(job_2_id)
        status_3 = await queue.get_job_status(job_3_id)

        print(f"Job 1 Status: {status_1.status.value}")
        print(f"Job 2 Status: {status_2.status.value}")
        print(f"Job 3 Status: {status_3.status.value}")

        # 4. WAIT FOR WORKER
        print("\n--- WAITING 5s FOR WORKER... ---")
        await asyncio.sleep(5)
        
        print("\n--- STATUS AFTER 5s ---")
        status_1 = await queue.get_job_status(job_1_id)
        status_2 = await queue.get_job_status(job_2_id)
        
        print(f"Job 1 Status (After 5s): {status_1.status.value}")
        print(f"Job 2 Status (After 5s): {status_2.status.value}")
        print(f"Job 3 Status (After 5s): {(await queue.get_job_status(job_3_id)).status.value}")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await queue.disconnect()

if __name__ == "__main__":
    asyncio.run(test_multi_node_dag())

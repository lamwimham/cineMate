"""
Integration Tests for JobQueue (PR #9 Fix)

Test Coverage:
- Sync/Async Redis client separation
- submit_job success without TypeError
- RQ Queue uses sync Redis client
- JobQueue metadata uses async Redis client
- Multi-job submission (rapid fire)
- Worker event publishing

PR #9 Fix: 'coroutine object is not subscriptable' error
Root cause: JobQueue initialized RQ with redis.asyncio client
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

# Import with proper separation
import redis
import redis.asyncio as async_redis
from rq import Queue

from cine_mate.infra.queue import JobQueue, JobQueueError, JobNotFoundError
from cine_mate.infra.schemas import JobType, JobStatus


class TestSyncAsyncRedisSeparation:
    """
    PR #9 核心修复: 同步/异步 Redis 客户端分离
    """

    @pytest.mark.asyncio
    async def test_connect_creates_separate_clients(self):
        """
        验证 connect() 创建两个分离的 Redis 客户端:
        - self.redis: async Redis for metadata
        - self.rq_queue.connection: sync Redis for RQ
        """
        queue = JobQueue(redis_url="redis://localhost:6379")

        with patch('redis.asyncio.from_url') as mock_async_from_url, \
             patch('redis.from_url') as mock_sync_from_url, \
             patch('rq.Queue') as mock_queue_class:

            # Setup mocks
            mock_async_redis = AsyncMock()
            mock_async_from_url.return_value = mock_async_redis

            mock_sync_redis = Mock()
            mock_sync_from_url.return_value = mock_sync_redis

            mock_queue = Mock()
            mock_queue_class.return_value = mock_queue

            await queue.connect()

            # Verify async Redis is used for self.redis
            mock_async_from_url.assert_called_once()
            assert queue.redis == mock_async_redis

            # Verify sync Redis is used for RQ Queue
            mock_sync_from_url.assert_called_once()
            mock_queue_class.assert_called_once_with(connection=mock_sync_redis)

    @pytest.mark.asyncio
    async def test_rq_queue_not_using_async_client(self):
        """
        边界场景: RQ Queue 不能使用 async Redis 客户端

        PR #9 修复前会抛出:
        TypeError: 'coroutine' object is not subscriptable

        这个测试验证修复后不会发生这个错误。
        """
        queue = JobQueue(redis_url="redis://localhost:6379")

        with patch('redis.asyncio.from_url') as mock_async_from_url, \
             patch('redis.from_url') as mock_sync_from_url:

            mock_async_redis = AsyncMock()
            mock_async_from_url.return_value = mock_async_redis

            mock_sync_redis = Mock()
            # Simulate RQ's internal sync operations (version check)
            mock_sync_redis.info = Mock(return_value={'redis_version': '7.0.0'})
            mock_sync_from_url.return_value = mock_sync_redis

            await queue.connect()

            # 验证: RQ Queue 使用的是 sync client, 不是 async
            assert hasattr(queue.rq_queue, 'connection')
            assert queue.rq_queue.connection == mock_sync_redis
            # 验证: async client 没有被传给 RQ
            assert queue.rq_queue.connection != mock_async_redis


class TestSubmitJobSuccess:
    """
    submit_job 成功入队测试
    """

    @pytest.mark.asyncio
    async def test_submit_job_no_type_error(self):
        """
        PR #9 修复验证: submit_job 不抛出 TypeError

        修复前错误:
        TypeError: 'coroutine' object is not subscriptable
        发生在 RQ 内部版本检查时 (redis.info() 被当成 async)
        """
        queue = JobQueue(redis_url="redis://localhost:6379")
        await queue.connect()

        # Mock RQ enqueue
        with patch.object(queue.rq_queue, 'enqueue') as mock_enqueue:
            mock_enqueue.return_value = Mock(id='test_job_001')

            # Mock Redis hset
            with patch.object(queue.redis, 'hset', new_callable=AsyncMock) as mock_hset, \
                 patch.object(queue.redis, 'expire', new_callable=AsyncMock) as mock_expire:

                mock_hset.return_value = 1
                mock_expire.return_value = True

                # 这个调用在修复前会抛出 TypeError
                job_id = await queue.submit_job(
                    run_id="run_001",
                    node_id="node_img",
                    job_type=JobType.TEXT_TO_IMAGE,
                    params={"prompt": "a cyberpunk city"}
                )

                # 验证成功
                assert job_id is not None
                assert job_id.startswith("job_")

    @pytest.mark.asyncio
    async def test_submit_job_metadata_stored_correctly(self):
        """
        验证 Job 元数据使用 async Redis 存储
        """
        queue = JobQueue(redis_url="redis://localhost:6379")
        await queue.connect()

        stored_data = {}

        async def mock_hset(key, mapping=None, **kwargs):
            if mapping:
                stored_data[key] = mapping
            return 1

        with patch.object(queue.redis, 'hset', new_callable=AsyncMock, side_effect=mock_hset), \
             patch.object(queue.redis, 'expire', new_callable=AsyncMock), \
             patch.object(queue.rq_queue, 'enqueue'):

            job_id = await queue.submit_job(
                run_id="run_002",
                node_id="node_vid",
                job_type=JobType.IMAGE_TO_VIDEO,
                params={"prompt": "animate scene", "duration": 5}
            )

            # 验证元数据存储在 async Redis
            job_key = f"job:{job_id}"
            assert job_key in stored_data
            assert stored_data[job_key]["run_id"] == "run_002"
            assert stored_data[job_key]["node_id"] == "node_vid"
            assert stored_data[job_key]["job_type"] == "image_to_video"


class TestMultiJobSubmission:
    """
    多任务快速提交边界场景
    """

    @pytest.mark.asyncio
    async def test_rapid_fire_submission(self):
        """
        边界场景: 快速连续提交多个任务

        PR #9 修复确保每个 submit_job 使用正确的客户端
        """
        queue = JobQueue(redis_url="redis://localhost:6379")
        await queue.connect()

        submitted_jobs = []

        with patch.object(queue.redis, 'hset', new_callable=AsyncMock) as mock_hset, \
             patch.object(queue.redis, 'expire', new_callable=AsyncMock), \
             patch.object(queue.rq_queue, 'enqueue') as mock_enqueue:

            mock_hset.return_value = 1
            mock_enqueue.return_value = Mock(id='mock_rq_job')

            # 快速提交 5 个任务
            for i in range(5):
                job_id = await queue.submit_job(
                    run_id=f"run_batch_{i}",
                    node_id=f"node_{i}",
                    job_type=JobType.TEXT_TO_IMAGE,
                    params={"prompt": f"scene {i}"}
                )
                submitted_jobs.append(job_id)

            # 验证所有任务都成功提交
            assert len(submitted_jobs) == 5
            assert all(j.startswith("job_") for j in submitted_jobs)
            # 验证 RQ enqueue 被调用 5 次
            assert mock_enqueue.call_count == 5

    @pytest.mark.asyncio
    async def test_concurrent_submission(self):
        """
        边界场景: 并发提交任务

        验证 sync/async 客户端分离在并发场景下仍然正常工作
        """
        queue = JobQueue(redis_url="redis://localhost:6379")
        await queue.connect()

        with patch.object(queue.redis, 'hset', new_callable=AsyncMock), \
             patch.object(queue.redis, 'expire', new_callable=AsyncMock), \
             patch.object(queue.rq_queue, 'enqueue'):

            # 并发提交 3 个任务
            tasks = [
                queue.submit_job(
                    run_id=f"run_concurrent_{i}",
                    node_id=f"node_c_{i}",
                    job_type=JobType.TEXT_TO_IMAGE,
                    params={"prompt": f"concurrent {i}"}
                )
                for i in range(3)
            ]

            job_ids = await asyncio.gather(*tasks)

            # 验证所有并发任务成功
            assert len(job_ids) == 3
            assert all(j.startswith("job_") for j in job_ids)


class TestJobStatusRetrieval:
    """
    任务状态检索测试
    """

    @pytest.mark.asyncio
    async def test_get_job_status_uses_async_redis(self):
        """
        验证 get_job_status 使用 async Redis 客户端
        """
        queue = JobQueue(redis_url="redis://localhost:6379")
        await queue.connect()

        mock_job_data = {
            "job_id": "job_test_001",
            "run_id": "run_001",
            "node_id": "node_img",
            "status": "queued",
            "progress": "0",
            "created_at": datetime.utcnow().isoformat(),
            "params": json.dumps({"prompt": "test"}),
        }

        with patch.object(queue.redis, 'exists', new_callable=AsyncMock, return_value=1), \
             patch.object(queue.redis, 'hgetall', new_callable=AsyncMock, return_value=mock_job_data):

            status = await queue.get_job_status("job_test_001")

            # 验证使用 async Redis
            queue.redis.exists.assert_called_once()
            queue.redis.hgetall.assert_called_once()

            assert status.job_id == "job_test_001"
            assert status.status == JobStatus.QUEUED

    @pytest.mark.asyncio
    async def test_job_not_found_raises_error(self):
        """
        边界场景: Job 不存在
        """
        queue = JobQueue(redis_url="redis://localhost:6379")
        await queue.connect()

        with patch.object(queue.redis, 'exists', new_callable=AsyncMock, return_value=0):
            with pytest.raises(JobNotFoundError):
                await queue.get_job_status("nonexistent_job")


class TestQueueStats:
    """
    Queue 统计测试
    """

    @pytest.mark.asyncio
    async def test_get_queue_stats_uses_async_scan(self):
        """
        验证 get_queue_stats 使用 async Redis scan_iter
        """
        queue = JobQueue(redis_url="redis://localhost:6379")
        await queue.connect()

        async def mock_scan_iter(pattern):
            # Simulate async iterator
            for key in ["job:001", "job:002"]:
                yield key

        with patch.object(queue.redis, 'scan_iter', side_effect=mock_scan_iter), \
             patch.object(queue.redis, 'hget', new_callable=AsyncMock, return_value="queued"):

            stats = await queue.get_queue_stats()

            # 验证使用了 async scan_iter
            assert "queued" in stats


class TestNotConnectedError:
    """
    未连接错误测试
    """

    @pytest.mark.asyncio
    async def test_submit_job_without_connect_raises(self):
        """
        边界场景: 未调用 connect() 就 submit_job
        """
        queue = JobQueue(redis_url="redis://localhost:6379")

        with pytest.raises(JobQueueError, match="Not connected"):
            await queue.submit_job(
                run_id="run_001",
                node_id="node_1",
                job_type=JobType.TEXT_TO_IMAGE,
                params={"prompt": "test"}
            )

    @pytest.mark.asyncio
    async def test_get_status_without_connect_raises(self):
        """
        边界场景: 未调用 connect() 就 get_job_status
        """
        queue = JobQueue(redis_url="redis://localhost:6379")

        with pytest.raises(JobQueueError, match="Not connected"):
            await queue.get_job_status("job_001")


class TestDisconnect:
    """
    断开连接测试
    """

    @pytest.mark.asyncio
    async def test_disconnect_closes_async_redis(self):
        """
        验证 disconnect() 关闭 async Redis 连接
        """
        queue = JobQueue(redis_url="redis://localhost:6379")

        with patch('redis.asyncio.from_url') as mock_async_from_url:
            mock_async_redis = AsyncMock()
            mock_async_redis.close = AsyncMock()
            mock_async_from_url.return_value = mock_async_redis

            with patch('redis.from_url'), patch('rq.Queue'):
                await queue.connect()
                await queue.disconnect()

                # 验证 async Redis 连接被关闭
                mock_async_redis.close.assert_called_once()
                assert not queue._connected
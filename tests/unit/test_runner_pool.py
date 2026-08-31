"""
Unit Tests for Runner Pool & Agent Allocation
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
sys.path.insert(0, os.path.abspath("apps/runner-agent/python"))
from runner_pool import RunnerPoolManager
from runner_agent import StepExecutionHarness, LogStreamChunker


class TestRunnerPool(unittest.TestCase):

    def setUp(self):
        self.pool = RunnerPoolManager(heartbeat_timeout_seconds=2)

    def test_runner_registration_and_allocation(self):
        self.pool.register_runner("agent-01", {"name": "k8s-runner-1", "tags": ["gpu", "linux"]})
        self.pool.register_runner("agent-02", {"name": "general-runner-2", "tags": ["linux"]})

        # Match specific tag
        assigned_gpu = self.pool.allocate_runner(required_tags=["gpu"])
        self.assertEqual(assigned_gpu, "agent-01")

        # Assign job
        self.pool.assign_job("agent-01", {"job_id": "job-101"})
        
        # Agent 01 is busy, next allocation for general should be agent 02
        assigned_next = self.pool.allocate_runner(required_tags=["linux"])
        self.assertEqual(assigned_next, "agent-02")

    def test_step_execution_harness(self):
        result = StepExecutionHarness.execute_script('python -c "print(12345)"')
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("12345", result["stdout"])

    def test_log_stream_chunker(self):
        raw = "\n".join(["Line 1", "Line 2", "Line 3"])
        chunks = list(LogStreamChunker.chunk_logs(raw))
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0]["content"], "Line 1")
        self.assertEqual(chunks[0]["seq"], 1)


if __name__ == "__main__":
    unittest.main()

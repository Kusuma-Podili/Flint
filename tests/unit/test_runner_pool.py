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
        self.pool.register_runner("agent-01", {"name": "k8s-runner", "tags": ["gpu"]})
        self.pool.register_runner("agent-02", {"name": "cpu-runner", "tags": ["linux"]})
        assigned = self.pool.allocate_runner(required_tags=["gpu"])
        self.assertEqual(assigned, "agent-01")

    def test_step_execution_harness(self):
        result = StepExecutionHarness.execute_script('python -c "print(99999)"')
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("99999", result["stdout"])

    def test_log_stream_chunker(self):
        raw = "\n".join(["L1", "L2"])
        chunks = list(LogStreamChunker.chunk_logs(raw))
        self.assertEqual(len(chunks), 2)


if __name__ == "__main__":
    unittest.main()

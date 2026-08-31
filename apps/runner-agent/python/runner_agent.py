"""
NexusOps Distributed Worker Daemon (`nexus-agent`)
"""
import subprocess
import time
import json
import os
from typing import Dict, Any, Generator


class StepExecutionHarness:
    """Executes containerized and shell pipeline steps with real-time log chunking."""

    @staticmethod
    def execute_script(script: str, env: Dict[str, str] = None, timeout_sec: int = 300) -> Dict[str, Any]:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        start_time = time.time()
        try:
            res = subprocess.run(
                script,
                shell=True,
                capture_output=True,
                text=True,
                env=merged_env,
                timeout=timeout_sec
            )
            duration = time.time() - start_time
            return {
                "exit_code": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "duration_seconds": duration,
                "timed_out": False
            }
        except subprocess.TimeoutExpired as te:
            return {
                "exit_code": -1,
                "stdout": te.stdout or "",
                "stderr": "Step timed out after limit",
                "duration_seconds": timeout_sec,
                "timed_out": True
            }


class LogStreamChunker:
    """Formats log streams with sequence IDs and timestamps for WebSockets."""

    @staticmethod
    def chunk_logs(raw_output: str, chunk_size: int = 1024) -> Generator[Dict[str, Any], None, None]:
        lines = raw_output.splitlines()
        for idx, line in enumerate(lines):
            yield {
                "seq": idx + 1,
                "timestamp": time.time(),
                "content": line
            }

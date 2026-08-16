import subprocess
import time
from typing import Dict, Any, Generator

class StepExecutionHarness:
    @staticmethod
    def execute_script(script: str, env_vars: Dict[str, str] = None, timeout_seconds: int = 300) -> Dict[str, Any]:
        start = time.time()
        res = subprocess.run(script, shell=True, capture_output=True, text=True, timeout=timeout_seconds)
        return {
            "exit_code": res.returncode,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "duration_ms": round((time.time() - start) * 1000, 2)
        }

class LogStreamChunker:
    @staticmethod
    def chunk_logs(raw_text: str, chunk_size: int = 100) -> Generator[Dict[str, Any], None, None]:
        lines = raw_text.splitlines()
        for idx, line in enumerate(lines):
            yield {
                "seq": idx + 1,
                "timestamp": time.time(),
                "content": line
            }

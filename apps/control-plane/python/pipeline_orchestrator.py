"""
NexusOps Distributed Pipeline Orchestrator & State Machine
"""
import time
import uuid
from typing import Dict, Any, List, Optional
from dag_engine import DAGResolver, VariableInterpolator


class PipelineExecutionEngine:
    """Manages full lifecycle of pipeline runs, matrix expansion, and step dispatch."""

    def __init__(self, runner_pool=None):
        self.runner_pool = runner_pool
        self.runs: Dict[str, Dict[str, Any]] = {}

    def trigger_pipeline(
        self,
        pipeline_def: Dict[str, Any],
        trigger_meta: Dict[str, Any],
        variables: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        steps = pipeline_def.get("steps", [])
        
        # Build DAG
        resolver = DAGResolver(steps)
        stages = resolver.get_execution_stages()

        context = {
            "env": pipeline_def.get("environment", {}),
            "vars": variables or {},
            "trigger": trigger_meta,
            "run_id": run_id
        }

        run_state = {
            "run_id": run_id,
            "pipeline_id": pipeline_def.get("id", "pipe-custom"),
            "status": "RUNNING",
            "stages": stages,
            "current_stage_index": 0,
            "step_results": {},
            "context": context,
            "created_at": time.time(),
            "started_at": time.time(),
            "finished_at": None
        }

        self.runs[run_id] = run_state
        return run_state

    def complete_step(self, run_id: str, step_id: str, exit_code: int, logs: str) -> Dict[str, Any]:
        run = self.runs.get(run_id)
        if not run:
            raise KeyError(f"Run ID '{run_id}' not found")

        status = "SUCCESS" if exit_code == 0 else "FAILED"
        run["step_results"][step_id] = {
            "step_id": step_id,
            "status": status,
            "exit_code": exit_code,
            "completed_at": time.time()
        }

        if exit_code != 0:
            run["status"] = "FAILED"
            run["finished_at"] = time.time()
            return run

        # Check if all steps in all stages finished
        all_completed = len(run["step_results"]) == sum(len(stage) for stage in run["stages"])
        if all_completed:
            run["status"] = "SUCCESS"
            run["finished_at"] = time.time()

        return run

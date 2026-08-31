from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class PipelineRun(BaseModel):
    id: str
    pipeline_id: str
    status: str
    started_at: Optional[float] = None
    finished_at: Optional[float] = None

class StepResult(BaseModel):
    step_id: str
    status: str
    exit_code: int

class IaCPlan(BaseModel):
    workspace_id: str
    resources_to_add: int
    resources_to_change: int
    resources_to_destroy: int

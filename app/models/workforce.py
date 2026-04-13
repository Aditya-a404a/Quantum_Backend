from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Shift(BaseModel):
    id: str
    startHour: int
    duration: int
    type: str  # "day", "night", "overtime"

class WorkforceRequest(BaseModel):
    num_employees: int = Field(default=25, ge=5, le=100)
    num_days: int = Field(default=7, ge=1, le=14)
    min_shifts_per_worker: int = Field(default=3, ge=0)
    max_shifts_per_worker: int = Field(default=5, ge=0)
    workers_per_shift: int = Field(default=3, ge=1)
    constraint_strictness: float = Field(default=0.8, ge=0.0, le=1.0)
    algorithm: str = Field(default="quantum") # "classical" or "quantum"

class SolverMetrics(BaseModel):
    violations: int
    coverageDeficit: int
    computeTimeMs: int
    confidence: float

class WorkforceResponse(BaseModel):
    assignments: Dict[int, List[Shift]]
    metrics: SolverMetrics
    internal_logic: List[str]
    algorithm_used: str

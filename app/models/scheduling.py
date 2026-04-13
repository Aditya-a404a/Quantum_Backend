from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SchedulingRequest(BaseModel):
    num_employees: int
    num_days: int
    min_shifts_per_worker: int
    max_shifts_per_worker: int
    workers_per_shift: int
    constraint_strictness: float
    algorithm: str = "quantum" # or "classical"

class Shift(BaseModel):
    id: str
    startHour: int
    duration: int
    type: str

class SolverMetrics(BaseModel):
    violations: int
    coverageDeficit: int
    computeTimeMs: int
    confidence: float

class SchedulingResponse(BaseModel):
    assignments: Dict[int, List[Shift]]
    metrics: SolverMetrics
    internal_logic: List[str]
    algorithm_used: str
    qubo_info: Dict[str, Any] # For the "Verbose" frontend

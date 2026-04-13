from fastapi import APIRouter, HTTPException
from ..models.scheduling import SchedulingRequest, SchedulingResponse
from ..solvers.scheduling import solve_scheduling_classical, solve_scheduling_quantum

router = APIRouter(
    prefix="/scheduling",
    tags=["scheduling"]
)

@router.post("/solve", response_model=SchedulingResponse)
async def solve_scheduling(request: SchedulingRequest):
    try:
        if request.algorithm == "quantum":
            return solve_scheduling_quantum(request)
        else:
            return solve_scheduling_classical(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

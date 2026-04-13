from fastapi import APIRouter, HTTPException
from ..models.workforce import WorkforceRequest, WorkforceResponse
from ..solvers.workforce import solve_workforce_classical, solve_workforce_quantum

router = APIRouter(
    prefix="/workforce",
    tags=["workforce"]
)

@router.post("/solve", response_model=WorkforceResponse)
async def solve_workforce(request: WorkforceRequest):
    try:
        if request.algorithm == "quantum":
            return solve_workforce_quantum(request)
        else:
            return solve_workforce_classical(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

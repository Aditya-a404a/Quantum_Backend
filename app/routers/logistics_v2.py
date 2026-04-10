from fastapi import APIRouter, HTTPException
from ..models.logistics_v2 import VrpRequestV2, VrpResponseV2, VrpResultV2
from ..solvers.v2.ortools_v2 import solve_vrp_ortools_v2
from ..solvers.v2.quantum_v2 import solve_vrp_quantum_v2
import time

router = APIRouter(tags=["logistics_v2"])

@router.post("/logistics/solve", response_model=VrpResponseV2)
async def solve_vrp_v2(request: VrpRequestV2):
    """
    Solves VRP V2 using both Classical (OR-Tools) and Quantum-Hybrid solvers.
    """
    try:
        depot_dict = {"id": request.depot.id, "lat": request.depot.lat, "lng": request.depot.lng}
        clients_list = [{"id": c.id, "lat": c.lat, "lng": c.lng} for c in request.coordinates]
        
        # 1. Classical Solve
        c_result = solve_vrp_ortools_v2(
            depot=depot_dict,
            clients=clients_list,
            num_vehicles=request.noOfTrucks
        )
        
        # 2. Quantum Solve
        q_result = solve_vrp_quantum_v2(
            depot=depot_dict,
            clients=clients_list,
            num_vehicles=request.noOfTrucks
        )
        
        return VrpResponseV2(
            classical=VrpResultV2(**c_result),
            quantum=VrpResultV2(**q_result)
        )
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

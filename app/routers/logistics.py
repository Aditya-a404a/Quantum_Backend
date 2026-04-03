from fastapi import APIRouter, HTTPException
from ..models.logistics import RoutingRequest, RoutingResponse, RouteSequence, ComparativeRoutingResponse

router = APIRouter(
    prefix="/logistics",
    tags=["logistics"],
)

@router.post("/solve", response_model=RoutingResponse)
async def solve_routing_problem(request: RoutingRequest):
    """
    Endpoint to solve the vehicle routing problem based on provided parameters.
    """
    try:
        # Format coordinates as a list of dictionaries
        coords_list = []
        depot_index = 0
        
        # Add depot as index 0
        coords_list.append({"id": request.depot.id, "lat": request.depot.lat, "lng": request.depot.lng})

        # Add remaining coordinates
        for i, coord in enumerate(request.coordinates):
            if coord.id != request.depot.id:
                coords_list.append({"id": coord.id, "lat": coord.lat, "lng": coord.lng})

        if request.algorithm.lower() == "classical":
            from ..solvers.classical import solve_classical
            result = solve_classical(
                coordinates=coords_list,
                depot_index=depot_index,
                no_of_trucks=request.noOfTrucks
            )
        else:
            from ..solvers.quantum import solve_quantum
            result = solve_quantum(
                coordinates=coords_list,
                depot_index=depot_index,
                no_of_trucks=request.noOfTrucks
            )

        # Map response
        response_routes = [
            RouteSequence(
                vehicle_id=r["vehicle_id"],
                path=r["path"],
                distance=r["distance"]
            )
            for r in result["routes"]
        ]

        return RoutingResponse(
            noOfSteps=result["noOfSteps"],
            routes=response_routes,
            internalLogicDetails=result["internalLogicDetails"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/solve-comparative", response_model=ComparativeRoutingResponse)
async def solve_comparative_routing(request: RoutingRequest):
    """
    Endpoint to solve the vehicle routing problem using both classical and quantum algorithms.
    """
    try:
        # Format coordinates identically for both
        coords_list = []
        depot_index = 0
        coords_list.append({"id": request.depot.id, "lat": request.depot.lat, "lng": request.depot.lng})
        for coord in request.coordinates:
            if coord.id != request.depot.id:
                coords_list.append({"id": coord.id, "lat": coord.lat, "lng": coord.lng})

        # Run Classical
        from ..solvers.classical import solve_classical
        c_res = solve_classical(coordinates=coords_list, depot_index=depot_index, no_of_trucks=request.noOfTrucks)
        classical_out = RoutingResponse(
            noOfSteps=c_res["noOfSteps"],
            routes=[RouteSequence(**r) for r in c_res["routes"]],
            internalLogicDetails=c_res["internalLogicDetails"]
        )

        # Run Quantum
        from ..solvers.quantum import solve_quantum
        q_res = solve_quantum(coordinates=coords_list, depot_index=depot_index, no_of_trucks=request.noOfTrucks)
        quantum_out = RoutingResponse(
            noOfSteps=q_res["noOfSteps"],
            routes=[RouteSequence(**r) for r in q_res["routes"]],
            internalLogicDetails=q_res["internalLogicDetails"]
        )

        return ComparativeRoutingResponse(
            classical=classical_out,
            quantum=quantum_out
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

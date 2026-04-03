from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

class Coordinate(BaseModel):
    id: Union[str, int]
    lat: float
    lng: float

class RoutingRequest(BaseModel):
    coordinates: List[Coordinate] = Field(..., description="List of all coordinates including clients and depot if applicable")
    noOfClients: int = Field(..., description="Number of clients to serve")
    depot: Coordinate = Field(..., description="Depot location")
    noOfTrucks: int = Field(..., description="Available number of trucks/vehicles")
    algorithm: str = Field(..., description="Algorithm to use (e.g., classical, quantum-hybrid)")
    additionalInfo: Optional[Dict[str, Any]] = Field(default=None, description="Any extra algorithm-specific parameters")

class RouteSequence(BaseModel):
    vehicle_id: Union[str, int]
    path: List[Union[str, int]]  # Sequence of location IDs
    distance: Optional[float] = None

class RoutingResponse(BaseModel):
    noOfSteps: int = Field(..., description="Number of iterative steps taken by the algorithm")
    routes: List[RouteSequence] = Field(..., description="Assigned routes for each vehicle")
    internalLogicDetails: Dict[str, Any] = Field(..., description="Detailed metrics, optimization scores, and metrics generated during the run")

class ComparativeRoutingResponse(BaseModel):
    classical: RoutingResponse
    quantum: RoutingResponse

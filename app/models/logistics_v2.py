from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class CoordinateV2(BaseModel):
    id: str
    lat: float
    lng: float
    name: Optional[str] = None

class VrpRequestV2(BaseModel):
    coordinates: List[CoordinateV2]
    depot: CoordinateV2
    noOfTrucks: int
    algorithm: str = "classical"

class RouteSequenceV2(BaseModel):
    truck_id: int
    sequence: List[str]  # List of coordinate IDs
    total_distance: float  # In meters or km
    total_duration: float  # In seconds
    geometry: Optional[str] = None  # Encoded polyline or GeoJSON string

class VrpResultV2(BaseModel):
    status: str
    routes: List[RouteSequenceV2]
    total_distance: float
    total_duration: float
    computation_time: float
    solver_metadata: Dict[str, Any] = {}

class VrpResponseV2(BaseModel):
    classical: VrpResultV2
    quantum: VrpResultV2

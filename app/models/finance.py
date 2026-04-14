from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PortfolioRequest(BaseModel):
    numAssets: int = Field(10, ge=2, le=50, description="Number of top assets to include in optimization")
    riskTolerance: float = Field(0.5, ge=0.0, le=1.0, description="User's risk tolerance (0 = low, 1 = high)")
    costFactor: float = Field(0.2, ge=0.0, le=1.0, description="Factor to adjust for transaction costs")

class Allocation(BaseModel):
    asset: str
    weight: float

class FrontierPoint(BaseModel):
    risk: float
    expectedReturn: float

class PortfolioResult(BaseModel):
    allocation: List[Allocation]
    expectedReturn: float
    risk: float
    sharpeRatio: float
    computeTimeMs: int
    costImpact: float
    pipeline_steps: Optional[List[str]] = None

class TrajectoryPoint(BaseModel):
    date: str
    classical: float
    quantum: float

class QuantumFidelity(BaseModel):
    state: str
    probability: float

class PortfolioResponse(BaseModel):
    frontierData: List[FrontierPoint]
    monteCarloData: Optional[List[FrontierPoint]] = None
    trajectoryData: Optional[List[TrajectoryPoint]] = None
    quantumFidelity: Optional[List[QuantumFidelity]] = None
    meanReturns: Optional[List[float]] = None
    covMatrix: Optional[List[List[float]]] = None
    classical: PortfolioResult
    quantum: PortfolioResult

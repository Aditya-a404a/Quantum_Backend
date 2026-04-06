from fastapi import APIRouter, HTTPException
from ..models.finance import (
    PortfolioRequest, PortfolioResponse, PortfolioResult, 
    Allocation, FrontierPoint, TrajectoryPoint, QuantumFidelity
)
from ..utils.data_loader import data_loader
from ..solvers.classical import solve_portfolio_classical
from ..solvers.quantum import solve_portfolio_quantum
import numpy as np
from typing import List

router = APIRouter(
    prefix="/finance",
    tags=["finance"],
)

@router.post("/solve", response_model=PortfolioResponse)
async def solve_portfolio(request: PortfolioRequest):
    """
    Endpoint to solve the portfolio optimization problem using real historical data.
    """
    try:
        # 1. Load data and metrics
        tickers, mean_returns, cov_matrix = data_loader.get_portfolio_metrics(request.numAssets)
        
        # 2. Run Classical Solver
        classical_raw = solve_portfolio_classical(
            tickers=tickers,
            mean_returns=mean_returns,
            cov_matrix=cov_matrix,
            risk_tolerance=request.riskTolerance
        )
        
        # 3. Run Quantum Solver
        quantum_raw = solve_portfolio_quantum(
            tickers=tickers,
            mean_returns=mean_returns,
            cov_matrix=cov_matrix,
            risk_tolerance=request.riskTolerance
        )
        
        # 4. Generate Efficient Frontier Data
        frontier_points = []
        for rt in np.linspace(0, 1, 12):
            res = solve_portfolio_classical(tickers, mean_returns, cov_matrix, rt)
            frontier_points.append(FrontierPoint(
                risk=res["risk"],
                expectedReturn=res["expectedReturn"]
            ))
        
        # 5. Generate Monte Carlo Samples
        monte_carlo = data_loader.get_monte_carlo_samples(tickers, mean_returns, cov_matrix, 300)
        
        # 6. Generate Historical Trajectory (Backtest)
        dates, price_series = data_loader.get_cumulative_returns(tickers, 252)
        
        # Get weight vectors from solvers
        c_weights = np.array([0.0]*len(tickers))
        for a in classical_raw["allocation"]:
            idx = tickers.index(a["asset"])
            c_weights[idx] = a["weight"] / 100
            
        q_weights = np.array([0.0]*len(tickers))
        for a in quantum_raw["allocation"]:
            idx = tickers.index(a["asset"])
            q_weights[idx] = a["weight"] / 100
            
        # Normalize weights to ensure 100% basis (even if small positions were filtered)
        c_weights /= (np.sum(c_weights) + 1e-12)
        q_weights /= (np.sum(q_weights) + 1e-12)
            
        # ─── 4. CALCULATE CUMULATIVE TRAJECTORY ───
        # price_series corresponds to tickers in reordered state
        c_series = np.dot(price_series, c_weights)
        q_series = np.dot(price_series, q_weights)
        
        trajectory_data = [
            TrajectoryPoint(date=dates[i], classical=round(float(c_series[i]) * 100, 4), quantum=round(float(q_series[i]) * 100, 4))
            for i in range(len(dates))
        ]
        
        # 7. Generate Quantum Fidelity (Simulated State Distribution)
        # 16 possible states represented as bitstrings
        q_fidelity = []
        for i in range(16):
            # Center the probability around the 'optimal' search state
            prob = np.exp(-((i - 8)**2) / 6.0) # Gaussian centered around state 8
            q_fidelity.append(QuantumFidelity(state=f"|{i:04b}⟩", probability=round(float(prob) * 45, 2)))
        
        # Adjust classical/quantum metrics based on costFactor
        classical_raw["costImpact"] *= request.costFactor
        quantum_raw["costImpact"] *= request.costFactor

        return PortfolioResponse(
            frontierData=frontier_points,
            monteCarloData=[FrontierPoint(risk=s["risk"], expectedReturn=s["return"]) for s in monte_carlo],
            trajectoryData=trajectory_data,
            quantumFidelity=q_fidelity,
            meanReturns=mean_returns.tolist(),
            covMatrix=cov_matrix.tolist(),
            classical=PortfolioResult(**classical_raw),
            quantum=PortfolioResult(**quantum_raw)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

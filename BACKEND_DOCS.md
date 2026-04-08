# Quantum Solutions API - Backend Documentation

## Project Overview
This repository provides the FastAPI backend service for the Quantum Logistics and Finance Demo. It implements both classical and quantum-hybrid optimization algorithms to solve Vehicle Routing Problems (VRP) and Portfolio Optimization.

### Core Technologies
- **Framework**: FastAPI
- **Language**: Python 3.10+
- **Optimization**: 
  - OR-Tools (Classical)
  - Qiskit / QAOA (Quantum-Hybrid)
  - NetworkX (Graph Algorithms)
  - Scikit-learn (KMeans Clustering)
- **Deployment**: Render (currently)

## Directory Structure
- `app/`: Main application logic.
  - `main.py`: Entry point, CORS configuration, and router inclusion.
  - `routers/`: API endpoints for `logistics` and `finance`.
  - `solvers/`: Implementation of core optimization logic.
    - `classical.py`: Uses OR-Tools for traditional VRP solving.
    - `quantum.py`: Implements QAOA-based hybrid solvers with hierarchical spectral sub-clustering.
  - `models/`: Pydantic schemas for request/response validation.
  - `utils/`: Common utilities for coordinate distance calculation.

## API Endpoints

### Logistics Service
- **Solve VRP**: `POST /api/v1/logistics/solve`
- **Solve Comparative**: `POST /api/v1/logistics/solve-comparative`
  - Runs both classical and quantum solvers and returns both results for comparison.

**Request Schema**:
```json
{
  "coordinates": [{"id": "...", "lat": 0, "lng": 0}],
  "noOfClients": 5,
  "depot": {"id": "...", "lat": 0, "lng": 0},
  "noOfTrucks": 3,
  "algorithm": "quantum"
}
```

### Finance Service
- **Portfolio Optimization**: `POST /api/v1/finance/optimize`
  - Optimizes asset allocation based on historical stock data (`all_stocks_5yr.csv`).

## Solver Logic breakdown

### Quantum-Hybrid VRP Solver
The `solve_quantum` function follows a sophisticated pipeline:
1. **Graph Construction**: Builds a Manhattan search space graph from coordinates.
2. **K-Means Clustering**: Partitions clients into high-level "Super Nodes".
3. **Spectral Sub-clustering**: Uses Fiedler vectors for hierarchical partitioning into sub-problems (at most 4 nodes each).
4. **QAOA Execution**: Maps each sub-problem to a Quadratic Program and solves using Qiskit's QAOA.
5. **Route Stitching**: Connects sub-problem solutions into a continuous vehicle route.

## Setup & installation

### Prerequisites
- Python 3.10 or higher.
- `pip` or `poetry`.

### Installation
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the server
```bash
python run.py
```
The API will be available at `http://localhost:8000`.

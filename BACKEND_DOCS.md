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
  - `routers/`: API endpoints for `logistics`, `finance`, and `scheduling`.
  - `solvers/`: Implementation of core optimization logic.
    - `classical.py`: Uses OR-Tools for traditional VRP solving.
    - `quantum.py`: Implements QAOA-based hybrid solvers.
    - `scheduling.py`: Implements QUBO-to-Ising formulation for workforce scheduling.
  - `models/`: Pydantic schemas for request/response validation.
  - `utils/`: Common utilities for data loading and calculations.

## API Endpoints

### Scheduling Service (NEW)
- **Solve Schedule**: `POST /api/v1/scheduling/solve`
  - High-fidelity workforce optimization implementing full QUBO mapping.

**Request Schema**:
```json
{
  "num_employees": 25,
  "num_days": 7,
  "min_shifts_per_worker": 3,
  "max_shifts_per_worker": 5,
  "workers_per_shift": 3,
  "constraint_strictness": 0.8,
  "algorithm": "quantum"
}
```

### Logistics Service
- **Solve VRP**: `POST /api/v1/logistics/solve`
... (existing) ...

## Solver Logic breakdown

### Scheduling QUBO Pipeline
The `scheduling.py` solver implements a specialized pipeline for Human Resource optimization:
1. **Variable Mapping**: Discretizes the schedule into $N \times D \times S$ binary variables (decision nodes).
2. **Penalty Formulation**: 
   - **Coverage (Hard)**: $( \sum x_{e,s} - K )^2$ ensures shift demand targets.
   - **Workload (Soft)**: $( \sum x_{d,s} - Target )^2$ balances employee hours.
   - **Adjacency (Hard)**: $P \cdot x_s \cdot x_{s+1}$ prevents back-to-back shift violations.
3. **Ising Transformation**: Maps binary variables $\{0,1\}$ to spin states $\{-1,1\}$ for QPU ingestion.
4. **Heuristic Emulation**: Uses energy minimization guided by Hamiltonian spin interactions to find the global minimum configuration.

### Quantum-Hybrid VRP Solver
... (existing) ...

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

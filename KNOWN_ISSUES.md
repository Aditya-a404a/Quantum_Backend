# Known Issues - Quantum Backend

## 1. Qiskit Compatibility
The Qiskit software stack can be sensitive to the Python version and underlying OS libraries. 
- **Issue**: Installation on some environments might fail due to `symengine` or `rust` dependency requirements.
- **Mitigation**: The `quantum.py` solver includes a "Digital Twin" fallback that simulates QAOA behavior if the library is not available.

## 2. Wide-Open CORS
Currently, `app/main.py` is configured with `allow_origins=["*"]`.
- **Security**: This should be restricted to the specific frontend domain in production to prevent Cross-Origin Request Forgery.

## 3. Lack of Authentication
The API endpoints currently have no authentication layer.
- **Risk**: Anyone with the endpoint URL can trigger computationally expensive quantum simulations.
- **Suggestion**: Implement an API key system or OAuth2 bearer tokens.

## 4. Algorithmic Constraints
- **KMeans**: The number of clusters is currently capped at 4 (`n_clusters = min(4, len(client_indices))`). This may lead to inefficient routes for maps with very large client counts.
- **Node Limit**: Individual sub-cluster sizes are capped at 4 for QAOA stability.

## 5. Deployment Latency
When hosted on free-tier platforms like Render, the service may spin down.
- **Effect**: Users may experience "Request Timeout" or long delays (>30s) on the first request.
- **Suggestion**: Use a "Keep Alive" service or upgrade to a paid tier.

## 6. Stock Data Dependency
The finance module depends on a local file `all_stocks_5yr.csv`.
- **Issue**: This file is large (~30MB) and manually managed.
- **Improvement**: Integrate with an external financial data provider API (e.g., Yahoo Finance).

## 7. High-Qubit Complexity (Scheduling)
The scheduling vertical allows up to 50 employees, which results in >1,000 binary variables.
- **Limitation**: Gate-based statevector simulation (O(2^N)) is physically impossible at this scale.
- **Behavior**: The `scheduling.py` solver uses a high-fidelity **Heuristic Emulation** (Simulated Annealing) to produce the Ground State results. This ensures demo responsiveness while perfectly mirroring the bitstring output of a real Hybrid QPU.
- **Recommendation**: For production-grade results on thousands of variables, use `LeapHybridCQMSampler` from D-Wave.

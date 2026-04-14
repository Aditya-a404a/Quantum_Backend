import os
import sys
import numpy as np

# Add the project root to sys.path
sys.path.append(r'c:\Users\adity\OneDrive\Documents\GitHub\Quantum_Backend')

try:
    from app.models.scheduling import SchedulingRequest
    from app.solvers.scheduling import solve_scheduling_quantum
    
    mock_request = SchedulingRequest(
        num_employees=2,
        num_days=2,
        min_shifts_per_worker=1,
        max_shifts_per_worker=5,
        workers_per_shift=1,
        constraint_strictness=0.8,
        algorithm="quantum"
    )
    
    print("Testing Quantum Solver...")
    response = solve_scheduling_quantum(mock_request)
    print("Success!")
    print(f"Algorithm: {response.algorithm_used}")
    print(f"Internal Logic Steps: {len(response.internal_logic)}")
    print(f"Energy State: {response.qubo_info['energy_state']}")
    print(f"Hamiltonian Snippet: {response.qubo_info['hamiltonian']}")

except Exception as e:
    import traceback
    traceback.print_exc()

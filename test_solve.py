from app.solvers.classical import solve_classical
from app.solvers.quantum import solve_quantum

coordinates = [
    {"id": "c1", "lat": 40.7128, "lng": -74.0060},
    {"id": "c2", "lat": 40.7138, "lng": -74.0070},
    {"id": "c3", "lat": 40.7148, "lng": -74.0080},
    {"id": "c4", "lat": 40.7158, "lng": -74.0090},
]

try:
    res_c = solve_classical(coordinates, 0, 2)
    print("CLASSICAL SUCCESS:", res_c)
except Exception as e:
    print("CLASSICAL FAILED:", e)

try:
    res_q = solve_quantum(coordinates, 0, 2)
    print("QUANTUM SUCCESS:", res_q)
except Exception as e:
    print("QUANTUM FAILED:", e)

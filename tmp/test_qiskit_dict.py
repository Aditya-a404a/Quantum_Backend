import os
import sys

# Add the project root to sys.path
sys.path.append(r'c:\Users\adity\OneDrive\Documents\GitHub\Quantum_Backend')

try:
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.converters import QuadraticProgramToQubo
    
    qp = QuadraticProgram("test")
    qp.binary_var(name="x")
    qp.binary_var(name="y")
    qp.minimize(quadratic={("x", "y"): 1}, linear={"x": 2})
    
    converter = QuadraticProgramToQubo()
    qubo = converter.convert(qp)
    
    print("Linear Dict:", qubo.objective.linear.to_dict())
    print("Quadratic Dict:", qubo.objective.quadratic.to_dict())

except Exception as e:
    import traceback
    traceback.print_exc()

import os
import sys

# Add the project root to sys.path
sys.path.append(r'c:\Users\adity\OneDrive\Documents\GitHub\Quantum_Backend')

try:
    from qiskit_optimization import QuadraticProgram
    
    qp = QuadraticProgram("test")
    qp.binary_var(name="x")
    qp.binary_var(name="y")
    
    print("Methods:", [m for m in dir(qp) if 'index' in m or 'var' in m])
    print("X index:", qp.get_variable("x").name, "???")
    # Looking for a way to get index from name
    v = qp.get_variable("x")
    # In some versions it's an object with an index attribute
    # In others it might be a list
    print("Variable object:", v)

except Exception as e:
    import traceback
    traceback.print_exc()

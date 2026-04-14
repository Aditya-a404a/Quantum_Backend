print("Importing math, time, typing...")
import math, time, typing
print("Importing numpy...")
import numpy as np
print("Importing networkx...")
import networkx as nx
print("Importing sklearn.cluster...")
from sklearn.cluster import KMeans
print("Importing fastapi...")
from fastapi import FastAPI
print("Importing routers...")
try:
    print("Importing logistics...")
    from app.routers import logistics
    print("Importing finance...")
    from app.routers import finance
    print("Importing logistics_v2...")
    from app.routers import logistics_v2
    print("Importing workforce...")
    from app.routers import workforce
    print("Importing scheduling...")
    from app.routers import scheduling
except Exception as e:
    print(f"FAILED: {e}")
print("DONE")

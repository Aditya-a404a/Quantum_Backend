from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import logistics, finance, logistics_v2, workforce, scheduling

app = FastAPI(
    title="Quantum Solutions API",
    description="Backend service for Quantum Logistics, Finance, and Workforce Demo",
    version="2.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logistics.router, prefix="/api/v1")
app.include_router(finance.router, prefix="/api/v1")
app.include_router(logistics_v2.router, prefix="/api/v2")
app.include_router(workforce.router, prefix="/api/v1")
app.include_router(scheduling.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Quantum Solutions API is running"}

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import init_db
from app.api import (
    merchants_router,
    products_router,
    inventory_router,
    policies_router,
    negotiations_router,
    payments_router,
    analytics_router,
    audit_router,
    failure_router,
    simulation_router
)

app = FastAPI(
    title="AI Agent Negotiator API",
    version=settings.APP_VERSION,
    description="Merchant-side Agentic Commerce & Deterministic Negotiation Engine for AI-to-AI Commerce."
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "architecture": "AI Negotiates. Code Controls the Money. Payment Provider Verifies."
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "gemini_model": settings.GEMINI_MODEL,
        "payment_sandbox": "mock" if settings.USE_MOCK_PAYMENTS else "razorpay_live"
    }

# Register API Routers
app.include_router(merchants_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(inventory_router, prefix="/api")
app.include_router(policies_router, prefix="/api")
app.include_router(negotiations_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(failure_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

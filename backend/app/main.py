import os
os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
import backend.app.models.entities  # Ensure all models are registered with Base metadata
from backend.app.api.auth import router as auth_router
from backend.app.api.properties import router as properties_router
from backend.app.api.bookings import router as bookings_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.reviews import router as reviews_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.ml_ops import router as ml_ops_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api/v1
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(properties_router, prefix=settings.API_V1_STR)
app.include_router(bookings_router, prefix=settings.API_V1_STR)
app.include_router(recommendations_router, prefix=settings.API_V1_STR)
app.include_router(reviews_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(ml_ops_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "tagline": "Find the right space, for exactly as long as you need.",
        "version": "1.0.0",
        "docs_url": f"{settings.API_V1_STR}/docs",
        "api_v1_prefix": settings.API_V1_STR,
        "status": "online",
    }

@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": "local_development",
        "version": "1.0.0",
    }

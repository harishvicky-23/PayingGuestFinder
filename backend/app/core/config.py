import os
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # h:\PayingGuest\backend
PROJECT_ROOT = BASE_DIR.parent  # h:\PayingGuest

class Settings(BaseSettings):
    PROJECT_NAME: str = "StayNearby"
    PROJECT_DESCRIPTION: str = "AI-Powered Short-Duration Home Rental Marketplace with MLOps"
    API_V1_STR: str = "/api/v1"
    
    # Security & Auth (Configurable via ENV, default for local development demo)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "staynearby-super-secret-dev-jwt-key-2026-change-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for dev convenience
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT}/staynearby.db")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # MLOps & Storage Paths
    ARTIFACTS_DIR: Path = BASE_DIR / "artifacts"
    DATA_DIR: Path = BASE_DIR / "data"
    MLRUNS_DIR: Path = PROJECT_ROOT / "mlruns"
    MLFLOW_TRACKING_URI: str = f"sqlite:///{PROJECT_ROOT}/mlflow.db"
    
    # Recommender baseline default weights
    WEIGHT_LOCATION: float = 0.25
    WEIGHT_PRICE: float = 0.20
    WEIGHT_AMENITIES: float = 0.20
    WEIGHT_PREFERENCES: float = 0.15
    WEIGHT_RATING: float = 0.10
    WEIGHT_DURATION: float = 0.10

    class Config:
        env_file = f"{PROJECT_ROOT}/.env"
        case_sensitive = True

settings = Settings()

# Ensure directories exist
settings.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.MLRUNS_DIR.mkdir(parents=True, exist_ok=True)

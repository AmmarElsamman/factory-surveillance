"""
Configuration management 
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    #API
    api_host: str = os.getenv('API_HOST', '0.0.0.0')
    api_port: int = int(os.getenv('API_PORT', '8000'))
    api_prefix: str = str(os.getenv('API_PREFIX', '/api/v1'))
    
    # Database
    database_host: str = os.getenv('DATABASE_HOST', 'localhost')
    database_port: str = os.getenv('DATABASE_PORT', '5432')
    database_name: str = os.getenv('DATABASE_NAME', 'factory_surveillance_db')
    database_user: str = os.getenv('DATABASE_USER', 'surveillance_app')
    database_password: str = os.getenv('DATABASE_PASSWORD', 'djr6w32g')
    
    # Re-ID Thresholds
    REID_VERY_HIGH_THRESHOLD: float = float(os.getenv('REID_VERY_HIGH_THRESHOLD', '0.95'))
    REID_HIGH_THRESHOLD: float = float(os.getenv('REID_HIGH_THRESHOLD', '0.90'))
    REID_ACCEPT_THRESHOLD: float = float(os.getenv('REID_ACCEPT_THRESHOLD', '0.85'))
    REID_POSSIBLE_THRESHOLD: float = float(os.getenv('REID_POSSIBLE_THRESHOLD', '0.75'))
    
    # Tracking
    TRACK_TIMEOUT_SECONDS: int = int(os.getenv('TRACK_TIMEOUT_SECONDS', '300'))  # 5 minutes
    TRACK_LOST_SECONDS: int = int(os.getenv('TRACK_LOST_SECONDS', '60'))  # 1 minute
    
    # Alerts
    INTRUDER_GRACE_PERIOD_SECONDS: int = int(os.getenv('INTRUDER_GRACE_PERIOD_SECONDS', '120'))  # 2 minutes
    HELMET_VIOLATION_DURATION_SECONDS: int = int(os.getenv('HELMET_VIOLATION_DURATION_SECONDS', '15'))
    
    # Embedding
    EMBEDDING_DIMENSION: int = int(os.getenv('EMBEDDING_DIMENSION', '512'))
    MAX_EMBEDDINGS_PER_WORKER: int = int(os.getenv('MAX_EMBEDDINGS_PER_WORKER', '10'))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/reid_service.log')
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()
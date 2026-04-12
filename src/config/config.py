"""
Configuration management for Re-ID system
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'factory_surveillance')
    DATABASE_USER = os.getenv('DATABASE_USER', 'surveillance_app')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'your_password')
    
    # API
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '8000'))
    
    # Re-ID Thresholds
    REID_STRONG_MATCH_THRESHOLD = float(os.getenv('REID_STRONG_MATCH_THRESHOLD', '0.90'))
    REID_ACCEPT_MATCH_THRESHOLD = float(os.getenv('REID_ACCEPT_MATCH_THRESHOLD', '0.85'))
    REID_POSSIBLE_MATCH_THRESHOLD = float(os.getenv('REID_POSSIBLE_MATCH_THRESHOLD', '0.75'))
    
    # Tracking
    TRACK_TIMEOUT_SECONDS = int(os.getenv('TRACK_TIMEOUT_SECONDS', '300'))  # 5 minutes
    TRACK_LOST_SECONDS = int(os.getenv('TRACK_LOST_SECONDS', '60'))  # 1 minute
    
    # Intruder Detection
    INTRUDER_GRACE_PERIOD_SECONDS = int(os.getenv('INTRUDER_GRACE_PERIOD_SECONDS', '120'))  # 2 minutes
    
    # Embedding
    EMBEDDING_DIMENSION = int(os.getenv('EMBEDDING_DIMENSION', '512'))
    MAX_EMBEDDINGS_PER_WORKER = int(os.getenv('MAX_EMBEDDINGS_PER_WORKER', '5'))
    
    # Alert Settings
    HELMET_VIOLATION_DURATION_SECONDS = int(os.getenv('HELMET_VIOLATION_DURATION_SECONDS', '10'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/reid_service.log')

config = Config()
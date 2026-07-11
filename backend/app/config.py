"""
Configuration - Deterministic Mode Enabled
Temperature = 0, Seed = 40
"""

from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # === MODEL SETTINGS (Deterministic) ===
    MODEL_NAME: str = "llama3.2:7b"
    MODEL_TEMPERATURE: float = 0.0  # Deterministic
    MODEL_SEED: int = 40  # Fixed seed for reproducibility
    MODEL_TOP_P: float = 0.95
    MODEL_TOP_K: int = 40
    MODEL_MAX_TOKENS: int = 4096
    MODEL_FREQUENCY_PENALTY: float = 0.0
    MODEL_PRESENCE_PENALTY: float = 0.0
    
    # === CACHE ===
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 86400  # 24 hours
    CACHE_MAX_SIZE: int = 10000
    CACHE_REDIS_URL: Optional[str] = None
    
    # === API ===
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    CORS_ORIGINS: List[str] = ["*"]
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # === DATABASE ===
    DATABASE_URL: str = "sqlite:///./ai_platform.db"
    
    # === OLLAMA ===
    OLLAMA_HOST: str = "localhost"
    OLLAMA_PORT: int = 11434
    
    # === ACCURACY ===
    ACCURACY_THRESHOLD: float = 0.85
    ENABLE_ACCURACY_SCORING: bool = True
    
    # === DEBATE ===
    DEBATE_MAX_ROUNDS: int = 10
    DEBATE_MAX_PARTICIPANTS: int = 5
    
    # === LOGGING ===
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "ai_platform.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

config = Settings()

# Validate deterministic settings
assert config.MODEL_TEMPERATURE == 0.0, "Temperature must be 0 for deterministic mode"
assert config.MODEL_SEED == 40, "Seed must be 40 for reproducibility"

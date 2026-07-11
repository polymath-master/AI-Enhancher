"""
Pydantic Schemas - All Data Models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ModelSettings(BaseModel):
    """Model inference settings - Deterministic by default"""
    temperature: float = Field(0.0, ge=0.0, le=2.0, description="0 = deterministic")
    seed: Optional[int] = Field(40, ge=0, description="Fixed seed = 40")
    top_p: float = Field(0.95, ge=0.0, le=1.0)
    top_k: int = Field(40, ge=1)
    max_tokens: int = Field(4096, ge=1, le=8192)
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(0.0, ge=-2.0, le=2.0)
    deterministic: bool = Field(True, description="Always True for production")
    
    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 0.0,
                "seed": 40,
                "top_p": 0.95,
                "max_tokens": 4096
            }
        }

class PromptRequest(BaseModel):
    """Chat/Generation request"""
    prompt: str = Field(..., min_length=1, max_length=32000)
    settings: Optional[ModelSettings] = ModelSettings()
    system_prompt: Optional[str] = None
    cache_enabled: bool = True
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()
    
    @validator('settings')
    def validate_settings(cls, v):
        if v and v.temperature != 0.0:
            v.temperature = 0.0  # Force deterministic
        if v and v.seed != 40:
            v.seed = 40  # Force seed 40
        return v

class PromptResponse(BaseModel):
    """Generation response"""
    request_id: str
    response: str
    cached: bool = False
    processing_time: float
    tokens_used: int = 0
    model: str
    temperature: float = 0.0
    seed: int = 40
    accuracy_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)

class DebateRequest(BaseModel):
    """Multi-perspective debate request"""
    topic: str = Field(..., min_length=3, max_length=500)
    num_rounds: int = Field(3, ge=1, le=10)
    num_participants: int = Field(2, ge=2, le=5)
    perspectives: Optional[List[str]] = None
    settings: Optional[ModelSettings] = ModelSettings()
    
    @validator('settings')
    def validate_settings(cls, v):
        if v:
            v.temperature = 0.0
            v.seed = 40
        return v

class DebateRound(BaseModel):
    """Single debate round"""
    round_num: int
    speaker: str
    argument: str
    counter_arguments: Optional[List[Dict[str, str]]] = None

class DebateResponse(BaseModel):
    """Complete debate response"""
    request_id: str
    topic: str
    rounds: List[DebateRound]
    summary: Optional[str] = None
    winner: Optional[str] = None
    accuracy_score: float
    processing_time: float
    total_tokens: int = 0

class AccuracyScore(BaseModel):
    """Accuracy scoring result"""
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    breakdown: Dict[str, float]
    suggestions: Optional[List[str]] = None

class SystemMetrics(BaseModel):
    """System performance metrics"""
    uptime: float
    requests_total: int
    avg_latency: float
    cache_hit_rate: float
    cache_size: int
    model_loaded: bool
    memory_usage_mb: float
    cpu_usage_percent: float

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model: str
    temperature: float
    seed: int
    uptime: float
    cache_size: int

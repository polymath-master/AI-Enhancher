"""
🚀 AI Platform - Production Server
Temperature = 0, Seed = 40 (Deterministic)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import time
from datetime import datetime

from app.config import config
from app.services.ollama import ollama_service
from app.services.cache import cache_service
from app.services.debate import debate_service
from app.services.accuracy import accuracy_service
from app.api.routes import router
from app.api.websocket import websocket_endpoint
from app.utils.logger import logger

# Request tracking for metrics
request_counts = {}
avg_latency = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown events"""
    logger.info("=" * 60)
    logger.info("🚀 AI PLATFORM STARTING")
    logger.info(f"📌 Model: {config.MODEL_NAME}")
    logger.info(f"🌡️  Temperature: {config.MODEL_TEMPERATURE} (Deterministic)")
    logger.info(f"🌱 Seed: {config.MODEL_SEED} (Fixed)")
    logger.info("=" * 60)
    
    # Initialize services
    await ollama_service.initialize()
    await cache_service.initialize()
    logger.info("✅ All services initialized")
    
    # Start background tasks
    asyncio.create_task(background_metrics())
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AI Platform...")
    await ollama_service.shutdown()

async def background_metrics():
    """Background task for metrics collection"""
    while True:
        await asyncio.sleep(60)
        stats = await cache_service.get_stats()
        logger.info(f"📊 Cache: {stats}")

app = FastAPI(
    title="AI Platform Pro",
    description="Production-grade LLM inference with deterministic output",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")
app.websocket("/ws")(websocket_endpoint)

@app.get("/")
async def root():
    return {
        "name": "AI Platform Pro",
        "version": "2.0.0",
        "status": "online",
        "model": config.MODEL_NAME,
        "temperature": config.MODEL_TEMPERATURE,
        "seed": config.MODEL_SEED,
        "deterministic": True,
        "features": ["chat", "debate", "accuracy", "streaming", "caching"]
    }

@app.get("/health")
async def health():
    """Health check for Oracle load balancer"""
    ollama_health = await ollama_service.health_check()
    return {
        "status": "healthy" if ollama_health else "degraded",
        "model": config.MODEL_NAME,
        "temperature": config.MODEL_TEMPERATURE,
        "seed": config.MODEL_SEED,
        "uptime": time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0,
        "cache_size": len(cache_service._cache)
    }

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Track latency
    avg_latency.append(process_time)
    if len(avg_latency) > 1000:
        avg_latency.pop(0)
    
    return response

@app.on_event("startup")
async def startup_event():
    app.state.start_time = time.time()
    logger.info("✅ Server started successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        reload=False
    )

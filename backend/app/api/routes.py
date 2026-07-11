"""
REST API Routes - All Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List
import json

from app.models.schemas import (
    PromptRequest, PromptResponse, DebateRequest, DebateResponse,
    SystemMetrics, HealthResponse
)
from app.services.ollama import ollama_service
from app.services.cache import cache_service
from app.services.debate import debate_service
from app.services.accuracy import accuracy_service
from app.utils.logger import logger

router = APIRouter()

@router.post("/generate", response_model=PromptResponse)
async def generate(request: PromptRequest):
    """
    Generate a response with deterministic settings (Temp=0, Seed=40)
    """
    logger.info(f"📝 Generate request: {request.request_id[:8]} | {len(request.prompt)} chars")
    
    # Check cache
    if request.cache_enabled:
        cached = await cache_service.get(request.prompt)
        if cached:
            logger.info(f"💾 Cache hit: {request.request_id[:8]}")
            return PromptResponse(
                request_id=request.request_id,
                response=cached,
                cached=True,
                processing_time=0.0,
                tokens_used=0,
                model=ollama_service.model_name,
                temperature=0.0,
                seed=40
            )
    
    # Generate
    try:
        response = await ollama_service.generate(
            request.prompt,
            request.settings,
            request.system_prompt
        )
        
        # Cache
        if request.cache_enabled:
            await cache_service.set(request.prompt, response.response)
        
        # Score accuracy
        if config.ENABLE_ACCURACY_SCORING:
            accuracy = await accuracy_service.score_response(
                request.prompt,
                response.response
            )
            response.accuracy_score = accuracy.score
        
        logger.info(f"✅ Generated: {request.request_id[:8]} | {response.tokens_used} tokens | {response.processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_generate(request: PromptRequest):
    """
    Stream response with real-time tokens
    """
    async def generate_stream():
        try:
            async for chunk in ollama_service.stream_generate(
                request.prompt,
                request.settings,
                request.system_prompt
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@router.post("/debate", response_model=DebateResponse)
async def debate(request: DebateRequest):
    """
    Multi-perspective debate with deterministic settings
    """
    logger.info(f"🎭 Debate: {request.topic} | {request.num_rounds} rounds")
    
    try:
        result = await debate_service.conduct_debate(request)
        logger.info(f"✅ Debate complete: {result.processing_time:.2f}s")
        return result
    except Exception as e:
        logger.error(f"❌ Debate failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics():
    """
    Get system metrics
    """
    from app.main import avg_latency
    
    cache_stats = await cache_service.get_stats()
    ollama_stats = ollama_service.get_stats()
    
    avg_lat = sum(avg_latency) / len(avg_latency) if avg_latency else 0
    
    return {
        "cache": cache_stats,
        "ollama": ollama_stats,
        "avg_latency": avg_lat,
        "requests": ollama_stats.get('total_requests', 0),
        "deterministic": {
            "temperature": 0.0,
            "seed": 40,
            "mode": "fixed"
        }
    }

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    ollama_health = await ollama_service.health_check()
    return HealthResponse(
        status="healthy" if ollama_health else "degraded",
        model=ollama_service.model_name,
        temperature=0.0,
        seed=40,
        uptime=time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0,
        cache_size=len(cache_service._cache)
    )

@router.post("/cache/clear")
async def clear_cache():
    """
    Clear cache
    """
    await cache_service.clear()
    return {"status": "cache cleared"}

@router.get("/accuracy/{request_id}")
async def get_accuracy(request_id: str):
    """
    Get accuracy score for a previous request
    """
    # TODO: Store accuracy scores in database
    return {"status": "pending"}

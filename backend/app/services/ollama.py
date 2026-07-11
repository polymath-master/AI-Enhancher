"""
Ollama Service - Deterministic Mode (Temp=0, Seed=40)
"""

import ollama
import time
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
from datetime import datetime

from app.config import config
from app.models.schemas import ModelSettings, PromptResponse
from app.utils.logger import logger

class OllamaService:
    def __init__(self):
        self.client = None
        self.model_name = config.MODEL_NAME
        self.is_ready = False
        self.total_requests = 0
        self.total_tokens = 0
        self.avg_latency = 0.0
    
    async def initialize(self):
        """Initialize Ollama client and warm up model"""
        try:
            self.client = ollama.AsyncClient(
                host=f"http://{config.OLLAMA_HOST}:{config.OLLAMA_PORT}"
            )
            
            # Check if model exists
            models = await self.client.list()
            model_names = [m['name'] for m in models.get('models', [])]
            
            if self.model_name not in model_names:
                logger.warning(f"⚠️ Model {self.model_name} not found, pulling...")
                await self._pull_model()
            
            # Warm up
            await self._warmup()
            self.is_ready = True
            logger.info(f"✅ Ollama ready | Model: {self.model_name}")
            logger.info(f"🌡️  Temperature: {config.MODEL_TEMPERATURE} (Deterministic)")
            logger.info(f"🌱 Seed: {config.MODEL_SEED} (Fixed)")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama: {e}")
            raise
    
    async def _pull_model(self):
        """Pull model if not available"""
        try:
            logger.info(f"📥 Pulling {self.model_name}...")
            async for progress in self.client.pull(model=self.model_name, stream=True):
                if 'status' in progress:
                    logger.info(f"  {progress['status']}")
            logger.info("✅ Model pulled successfully")
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
            raise
    
    async def _warmup(self):
        """Send dummy request to load model"""
        try:
            await self.client.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hello"}],
                options={
                    "temperature": 0.0,
                    "seed": 40,
                    "num_predict": 1
                }
            )
        except Exception as e:
            logger.warning(f"Warmup failed: {e}")
            await asyncio.sleep(2)
    
    async def generate(
        self,
        prompt: str,
        settings: ModelSettings,
        system_prompt: Optional[str] = None
    ) -> PromptResponse:
        """Generate response - Deterministic (Temp=0, Seed=40)"""
        start_time = time.time()
        
        if not self.is_ready:
            raise Exception("Model not ready")
        
        # Enforce deterministic settings
        settings.temperature = 0.0
        settings.seed = 40
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        options = {
            "temperature": 0.0,
            "seed": 40,
            "top_p": settings.top_p,
            "top_k": settings.top_k,
            "num_predict": settings.max_tokens,
            "frequency_penalty": settings.frequency_penalty,
            "presence_penalty": settings.presence_penalty,
            "num_ctx": 4096,  # Fixed context
        }
        
        try:
            response = await self.client.chat(
                model=self.model_name,
                messages=messages,
                options=options,
                stream=False
            )
            
            processing_time = time.time() - start_time
            
            # Update metrics
            self.total_requests += 1
            self.total_tokens += response.get('eval_count', 0)
            self.avg_latency = (self.avg_latency * (self.total_requests - 1) + processing_time) / self.total_requests
            
            return PromptResponse(
                request_id=str(id(response)),
                response=response['message']['content'],
                cached=False,
                processing_time=processing_time,
                tokens_used=response.get('eval_count', 0),
                model=self.model_name,
                temperature=0.0,
                seed=40
            )
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    async def stream_generate(
        self,
        prompt: str,
        settings: ModelSettings,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Streaming generation"""
        settings.temperature = 0.0
        settings.seed = 40
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        options = {
            "temperature": 0.0,
            "seed": 40,
            "top_p": settings.top_p,
            "top_k": settings.top_k,
            "num_predict": settings.max_tokens,
            "num_ctx": 4096,
        }
        
        try:
            async for chunk in await self.client.chat(
                model=self.model_name,
                messages=messages,
                options=options,
                stream=True
            ):
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
        except Exception as e:
            logger.error(f"Stream failed: {e}")
            yield f"Error: {str(e)}"
    
    async def health_check(self) -> bool:
        """Check if Ollama is running"""
        try:
            await self.client.list()
            return self.is_ready
        except:
            return False
    
    async def shutdown(self):
        """Clean shutdown"""
        self.is_ready = False
        logger.info("Ollama service shutdown")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "model": self.model_name,
            "temperature": 0.0,
            "seed": 40,
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "avg_latency": self.avg_latency,
            "is_ready": self.is_ready
        }

ollama_service = OllamaService()

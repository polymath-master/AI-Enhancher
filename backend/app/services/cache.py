"""
Cache Service - Memory + Redis (optional)
"""

import hashlib
import json
import time
from typing import Optional, Dict, Any
from collections import OrderedDict

from app.config import config
from app.utils.logger import logger

class CacheService:
    def __init__(self):
        self._cache = OrderedDict()
        self._ttl = {}
        self.hits = 0
        self.misses = 0
        self.max_size = config.CACHE_MAX_SIZE
        self.ttl = config.CACHE_TTL
        self.redis_client = None
    
    async def initialize(self):
        """Initialize cache (optional Redis)"""
        if config.CACHE_REDIS_URL:
            try:
                import redis.asyncio as redis
                self.redis_client = await redis.from_url(config.CACHE_REDIS_URL)
                await self.redis_client.ping()
                logger.info("✅ Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis unavailable: {e}")
                self.redis_client = None
        logger.info("✅ Cache service initialized")
    
    def _get_key(self, text: str) -> str:
        """Generate cache key from text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[str]:
        """Get from cache"""
        cache_key = self._get_key(key)
        
        # Check Redis first
        if self.redis_client:
            try:
                value = await self.redis_client.get(cache_key)
                if value:
                    self.hits += 1
                    return value.decode()
            except:
                pass
        
        # Check memory cache
        if cache_key in self._cache:
            # Check TTL
            if cache_key in self._ttl and self._ttl[cache_key] < time.time():
                del self._cache[cache_key]
                del self._ttl[cache_key]
                self.misses += 1
                return None
            
            # Move to end (LRU)
            self._cache.move_to_end(cache_key)
            self.hits += 1
            return self._cache[cache_key]
        
        self.misses += 1
        return None
    
    async def set(self, key: str, value: str):
        """Set in cache"""
        cache_key = self._get_key(key)
        
        # Set in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    cache_key,
                    self.ttl,
                    value
                )
            except:
                pass
        
        # Set in memory
        self._cache[cache_key] = value
        self._ttl[cache_key] = time.time() + self.ttl
        
        # LRU eviction
        if len(self._cache) > self.max_size:
            oldest = next(iter(self._cache))
            del self._cache[oldest]
            if oldest in self._ttl:
                del self._ttl[oldest]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            "size": len(self._cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate * 100:.1f}%",
            "ttl": self.ttl,
            "redis_enabled": bool(self.redis_client)
        }
    
    async def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._ttl.clear()
        if self.redis_client:
            try:
                await self.redis_client.flushall()
            except:
                pass
        logger.info("Cache cleared")

cache_service = CacheService()

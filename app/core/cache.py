from typing import Any, Optional, Dict, List
import json
import time
from redis import asyncio as aioredis
from app.core.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class Cache:
    """Redis-based cache implementation with enhanced features."""
    
    # Default TTL values (in seconds)
    DEFAULT_TTL = 3600  # 1 hour
    SHORT_TTL = 300     # 5 minutes
    LONG_TTL = 86400    # 24 hours
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with hit/miss tracking."""
        value = await self.redis.get(key)
        if value:
            self._stats["hits"] += 1
            logger.debug(f"Cache hit for key: {key}")
            return json.loads(value)
        
        self._stats["misses"] += 1
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: int = DEFAULT_TTL,
        tags: List[str] = None
    ) -> None:
        """Set value in cache with expiration and optional tags.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: TTL in seconds
            tags: Optional list of tags for invalidation
        """
        try:
            # Serialize value to JSON with custom encoder
            serialized_value = json.dumps(value, cls=DateTimeEncoder)
            
            # Store value
            await self.redis.set(
                key,
                serialized_value,
                ex=expire
            )
            
            # Store tags if provided
            if tags:
                tag_key = f"tags:{key}"
                await self.redis.sadd(tag_key, *tags)
                await self.redis.expire(tag_key, expire)
        except Exception as e:
            print(f"Error setting cache: {str(e)}")
            raise
        
        self._stats["sets"] += 1
        logger.debug(f"Cache set for key: {key} with TTL: {expire}s")
    
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        await self.redis.delete(key)
        # Also delete associated tags
        await self.redis.delete(f"tags:{key}")
        self._stats["deletes"] += 1
        logger.debug(f"Cache delete for key: {key}")
    
    async def invalidate_by_tag(self, tag: str) -> None:
        """Invalidate all keys associated with a tag."""
        # Get all keys with this tag
        pattern = f"tags:*"
        async for key in self.redis.scan_iter(match=pattern):
            if await self.redis.sismember(key, tag):
                # Get the actual cache key from the tag key
                cache_key = key.replace("tags:", "")
                await self.delete(cache_key)
                logger.info(f"Invalidated cache key {cache_key} by tag {tag}")
    
    async def invalidate_by_pattern(self, pattern: str) -> None:
        """Invalidate all keys matching a pattern."""
        async for key in self.redis.scan_iter(match=pattern):
            await self.delete(key)
            logger.info(f"Invalidated cache key {key} by pattern {pattern}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return self._stats.copy()
    
    async def clear_stats(self) -> None:
        """Clear cache statistics."""
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for a key in seconds."""
        ttl = await self.redis.ttl(key)
        return ttl if ttl > 0 else None

async def get_cache() -> Cache:
    """Get cache instance."""
    return Cache() 
from typing import List, Dict, Any, Optional
import json
import redis.asyncio as redis
from core.config import settings

redis_client = None

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
    return redis_client

async def get_menu_from_cache(branch: int) -> Optional[List[Dict[str, Any]]]:
    try:
        r = await get_redis()
        data = await r.get(f"menu:{branch}")
        if data:
            return json.loads(data)
    except Exception as e:
        print(f"Redis get error: {e}")
    return None

async def store_menu_in_cache(branch: int, menu: List[Dict[str, Any]]):
    try:
        r = await get_redis()
        await r.setex(
            f"menu:{branch}", 
            settings.REDIS_TTL, 
            json.dumps(menu, default=str)
        )
    except Exception as e:
        print(f"Redis store error: {e}")

# === In-Memory Cache for Reviews Menu (Redis-style logic) ===
_reviews_menu_cache: Optional[List[Dict[str, Any]]] = None
_cache_key = "reviews_menu"

async def get_reviews_menu_from_cache() -> Optional[List[Dict[str, Any]]]:
    """
    Get menu with reviews from cache.
    Uses in-memory cache (Redis-style logic).
    """
    global _reviews_menu_cache
    try:
        # Try Redis first if available
        r = await get_redis()
        data = await r.get(_cache_key)
        if data:
            return json.loads(data)
    except Exception:
        # Fallback to in-memory cache
        pass
    
    # Return in-memory cache if Redis fails
    return _reviews_menu_cache

async def store_reviews_menu_in_cache(menu: List[Dict[str, Any]]):
    """
    Store menu with reviews in cache.
    Uses in-memory cache (Redis-style logic).
    """
    global _reviews_menu_cache
    try:
        # Try Redis first if available
        r = await get_redis()
        await r.setex(
            _cache_key,
            settings.REDIS_TTL,
            json.dumps(menu, default=str)
        )
    except Exception:
        # Fallback to in-memory cache
        pass
    
    # Store in in-memory cache as fallback
    _reviews_menu_cache = menu

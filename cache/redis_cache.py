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

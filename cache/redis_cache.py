import redis.asyncio as redis
import json
from datetime import datetime
from core.config import settings

# === Initialize Redis Client ===
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

# === Default TTL (time-to-live) for cached items in seconds ===
TTL = settings.REDIS_TTL

# === JSON Serializer for Non-Serializable Objects ===
def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# === Retrieve Menu from Redis Cache ===
async def get_menu_from_cache(branch: int):
    key = f"menu:{branch}"
    data = await redis_client.get(key)
    return json.loads(data) if data else None

# === Store Menu in Redis Cache ===
async def store_menu_in_cache(branch: int, data):
    key = f"menu:{branch}"
    await redis_client.set(
        key,
        json.dumps(data, default=json_serializer),
        ex=TTL
    )

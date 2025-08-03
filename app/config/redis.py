import redis.asyncio as redis
import redis as sync_redis
from typing import Optional
from .index import settings  # Make sure settings has REDIS_HOST, REDIS_PORT, REDIS_DB

redis_client: Optional[redis.Redis] = None
sync_redis_client: Optional[sync_redis.Redis] = None

def get_sync_redis() -> sync_redis.Redis:
    global sync_redis_client
    if sync_redis_client is None:
        try:
            # Use REDIS_URL if available (for Render), otherwise use individual settings
            # if settings.REDIS_URL:
            #     sync_redis_client = sync_redis.from_url(
            #         settings.REDIS_URL,
            #         decode_responses=True
            #     )
            # else:
                # Add connection timeout and retry logic
            sync_redis_client = sync_redis.Redis(
                host='redis-17372.c100.us-east-1-4.ec2.redns.redis-cloud.com',
                port=17372,
                decode_responses=True,
                username="default",
                password="Z40EUY1m1JH7ohPsuh2Y5KqCZj5WCDgg",
            )
            # Test the connection
            sync_redis_client.ping()
            print(f"Successfully connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except sync_redis.ConnectionError as e:
            print(f"Redis connection error: {e}")
            print(f"Trying to connect to: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            # For development, create a mock Redis if connection fails
            sync_redis_client = None
        except Exception as e:
            print(f"Unexpected Redis error: {e}")
            sync_redis_client = None
    return sync_redis_client

async def close_redis() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None 
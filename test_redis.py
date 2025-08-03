#!/usr/bin/env python3
"""
Test Redis connection script
"""
import redis
import socket
from app.config.index import settings

def test_dns_resolution():
    """Test if the Redis hostname can be resolved"""
    try:
        # Check if it's already an IP address
        if all(part.isdigit() for part in settings.REDIS_HOST.split('.')):
            print(f"✅ Using IP address directly: {settings.REDIS_HOST}")
            return True
        
        ip = socket.gethostbyname(settings.REDIS_HOST)
        print(f"✅ DNS Resolution: {settings.REDIS_HOST} -> {ip}")
        return True
    except socket.gaierror as e:
        print(e)
        # print(f"❌ DNS Resolution failed: {e}")
        return False

def test_redis_connection():
    """Test Redis connection"""
    try:
        print(f"🔍 Testing Redis connection to {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        
        # Use the host directly (could be IP or hostname)
        print(f"Using host: {settings.REDIS_HOST}")
        
        r = redis.Redis(
    host='redis-17372.c100.us-east-1-4.ec2.redns.redis-cloud.com',
    port=17372,
    decode_responses=True,
    username="default",
    password="Z40EUY1m1JH7ohPsuh2Y5KqCZj5WCDgg",
)
        
        # Test connection
        r.ping()
        print("✅ Redis connection successful!")
        
        # Test basic operations
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        print(f"✅ Redis operations test: {value}")
        
        # Clean up
        r.delete('test_key')
        print("✅ Redis cleanup successful!")
        
        return True
        
    except redis.ConnectionError as e:
        print(e)
        print(f"❌ Redis connection failed: {e}")
        return False
    except Exception as e:
        print(e)
        print(f"❌ Unexpected error: {e}")
        return False

def test_redis_url():
    """Test Redis URL connection"""
    try:
        redis_url = f"redis://{settings.REDIS_USERNAME}:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        print(f"🔍 Testing Redis URL: {redis_url}")
        
        r = redis.from_url(redis_url, decode_responses=True)
        r.ping()
        print("✅ Redis URL connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Redis URL connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Redis Connection Test")
    print("=" * 50)
    
    # Test DNS resolution
    # dns_ok = test_dns_resolution()
    redis_ok = test_redis_connection()
    
    # if dns_ok:
    #     # Test Redis connection
        
    #     if not redis_ok:
    #         # Try URL method
    #         test_redis_url()
    # else:
    #     print("❌ Cannot proceed with Redis tests due to DNS resolution failure") 
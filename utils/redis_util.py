import redis
import logging
from config import REDIS_CONFIG, ENABLE_REDIS

def init_redis_client():
    """初始化Redis客户端"""
    if not ENABLE_REDIS:
        print("Redis连接已禁用，跳过连接")
        return None
    try:
        client = redis.Redis(**REDIS_CONFIG)
        client.ping()
        print("Redis连接成功")
        return client
    except Exception as e:
        logging.warning(f"Redis连接失败: {e}")
        return None

# 全局Redis客户端
redis_client = init_redis_client()
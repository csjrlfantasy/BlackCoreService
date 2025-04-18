import redis
import logging
from config import REDIS_CONFIG

def init_redis_client():
    """初始化Redis客户端"""
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
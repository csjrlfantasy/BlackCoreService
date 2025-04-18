import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 文件服务配置
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {
    'txt': 'text/plain',
    'pdf': 'application/pdf',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'jar': 'application/java-archive'
}

# Configuration file (optional)
# 修改数据库配置部分
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:heihe123456@localhost/heihe_mall'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'your_secret_key'

# 启用连接池配置
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 1800
}


# Redis配置
REDIS_CONFIG = {
    'host': '192.168.11.129',
    'port': 6379,
    'db': 0,
    'socket_connect_timeout': 3,
    'socket_timeout': 3,
    'retry_on_timeout': True
}


RABBITMQ_CONFIG = {
    'HOST': '192.168.11.129',
    'PORT': 5672,
    'USERNAME': 'qingyun',  # 将USERNAME改为USER以匹配代码中的检查
    'PASSWORD': 'heihe123456',
    'VIRTUAL_HOST': '/',
    'QUEUE_NAME': 'flash_sale_queue',
    'HEARTBEAT': 600,
    'BLOCKED_CONNECTION_TIMEOUT': 300
}
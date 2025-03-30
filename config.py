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
# 新增数据库配置
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:heihe123456@localhost/heihe_mall'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'your_secret_key'



# # 添加连接池配置
# SQLALCHEMY_ENGINE_OPTIONS = {
#     "pool_size": 10,              # 连接池的大小（默认值为 5）
#     "max_overflow": 20,           # 在连接池达到最大连接数后可以额外创建的连接数
#     "pool_timeout": 30,           # 获取连接的超时时间（秒）
#     "pool_recycle": 1800          # 连接回收时间（秒），防止连接被数据库服务器断开
# }
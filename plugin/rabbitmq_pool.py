import pika
from queue import Queue
from threading import Lock
import time
import logging

class RabbitMQConnectionPool:
    def __init__(self, config, max_size=50, min_size=10):  # 增大连接池大小
        self.config = config
        self.max_size = max_size
        self.min_size = min_size
        self._pool = Queue(max_size)
        self._lock = Lock()
        self._active_connections = 0
        self.logger = logging.getLogger(__name__)
        
        # 预热连接池
        for _ in range(min_size):
            self._add_connection()

    def _add_connection(self):
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(
                host=self.config['HOST'],
                port=self.config['PORT'],
                virtual_host=self.config['VIRTUAL_HOST'],
                credentials=pika.PlainCredentials(
                    self.config['USERNAME'],
                    self.config['PASSWORD']
                ),
                heartbeat=60,  # 增加心跳间隔
                blocked_connection_timeout=300,
                connection_attempts=5,  # 增加重试次数
                retry_delay=3,  # 增加重试间隔
                socket_timeout=10  # 增加socket超时
            ))
            self._pool.put(conn)
            self._active_connections += 1
            return True
        except Exception as e:
            self.logger.error(f"创建RabbitMQ连接失败: {e}")
            return False

    def get_connection(self, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if not self._pool.empty() or self._active_connections < self.max_size:
                    with self._lock:
                        if not self._pool.empty():
                            conn = self._pool.get()
                            if conn and not conn.is_closed:
                                return conn
                        if self._active_connections < self.max_size:
                            if self._add_connection():
                                return self._pool.get()
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"获取连接异常: {e}")
        raise TimeoutError("获取RabbitMQ连接超时")

    def release_connection(self, conn):
        if conn and not conn.is_closed:
            try:
                self._pool.put(conn)
            except:
                conn.close()
                self._active_connections -= 1
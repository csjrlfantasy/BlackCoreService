import socket
import threading
from datetime import datetime

class TCPServer:
    def __init__(self, host='0.0.0.0', port=5001):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.server.bind((host, port))
        self.server.listen(5)
        print(f"TCP Server started on {host}:{port}")

    def handle_client(self, client_socket):
        try:
            while True:
                request = client_socket.recv(1024).decode('utf-8').strip()
                if not request:
                    break
                
                # 处理请求并返回带时间戳的响应
                reversed_str = request[::-1]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                # 修改响应结尾符为!
                response = f"{request}|{reversed_str}|{timestamp}|success!"
                
                client_socket.send(response.encode('utf-8'))
        finally:
            client_socket.close()

    def start(self):
        while True:
            client_sock, addr = self.server.accept()
            print(f"Accepted connection from: {addr[0]}:{addr[1]}")
            client_handler = threading.Thread(
                target=self.handle_client,
                args=(client_sock,)
            )
            client_handler.start()

def start_tcp_server():
    server = TCPServer()
    server.start()

if __name__ == "__main__":
    start_tcp_server()
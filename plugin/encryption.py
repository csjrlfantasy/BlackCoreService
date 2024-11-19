from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os

SECRET_KEY = os.getenv('AES_SECRET_KEY', '23owendslgfvmswr').encode('utf-8')
SECRET_KEY = SECRET_KEY[:32].ljust(32, b'\0')  # 保证密钥为32字节（AES-256）

def pad(data):
    padding = 16 - (len(data) % 16)
    return data + (chr(padding) * padding).encode()

def unpad(data):
    padding = data[-1]
    return data[:-padding]

def encrypt_aes(data):
    data = pad(data.encode('utf-8'))
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_aes(data):
    encrypted_data = base64.b64decode(data)
    cipher = Cipher(algorithms.AES(SECRET_KEY), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    return unpad(decrypted_data).decode('utf-8')

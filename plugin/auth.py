from flask import jsonify
from models import User

def check_admin_role(token):
    if not token:
        return jsonify({"error": "Authorization token is missing"}), 401

    # 查找用户
    user = User.query.filter_by(token=token).first()

    if not user or user.role != 0:  # role == 0 表示管理员
        return jsonify({"error": "Unauthorized access. Admins only."}), 403

    return None  # 表示通过了检查

def extract_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    # 支持 "Bearer token" 格式
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]
    
    return auth_header  # 如果没有使用Bearer格式，直接返回整个header值
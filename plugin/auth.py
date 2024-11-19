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
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        return token[7:]
    else:
        return None
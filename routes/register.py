from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from flasgger import swag_from
from models import db, User

register_bp = Blueprint('register', __name__)


@register_bp.route('/register', methods=['POST'])
@swag_from({
    'summary': '用户注册接口',
    'description': 'Register a new user with username, password, and role.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'user1'},
                    'password': {'type': 'string', 'example': 'password123'},
                    'role': {'type': 'integer', 'example': 1, 'description': '0 for admin, 1 for customer (default)'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'examples': {
                'application/json': {
                    'message': 'User registered successfully!'
                }
            }
        },
        400: {
            'description': 'Error during registration'
        }
    }
})
def register():
    data = request.json

    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({"message": "用户名已存在"}), 400

    # 获取并加密密码
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    # 获取传递的角色，如果没有传递则默认设置为1（普通用户）
    role = data.get('role', 1)

    if role not in [0, 1]:  # 确保role字段只有0或1的值
        return jsonify({"message": "非法的角色Id"}), 400

    # 创建新用户
    new_user = User(username=data['username'], password_hash=hashed_password, token="", role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "用户注册成功!"}), 201

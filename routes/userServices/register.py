from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from flasgger import swag_from
from models import db, User

register_bp = Blueprint('register', __name__)

@register_bp.route('/user_services/register', methods=['POST'])
@swag_from({
    'summary': '用户注册',
    'tags': ['用户管理服务'],
    'description': 'Register a new user with username, password, and optional nickname.',
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
                    'nickname': {'type': 'string', 'example': ''}
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
                    'message': 'User registered successfully!',
                    'user_id': 1,
                    'nickname': ''
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
    existing_user = User.query.filter_by(username=data['username']).first()

    if existing_user:
        return jsonify({"message": "Username already exists!"}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    # 使用提供的昵称，若未提供则生成默认昵称
    nickname = data.get('nickname', None)
    if not nickname:
        nickname = User().generate_default_nickname()

    new_user = User(
        username=data['username'],
        password_hash=hashed_password,
        nickname=nickname,
        token=""
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully!",
        "user_id": new_user.id,
        "nickname": new_user.nickname
    }), 201

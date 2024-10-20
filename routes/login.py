from flask import Blueprint, request, jsonify, current_app  # 导入 current_app
from werkzeug.security import check_password_hash
from flasgger import swag_from
import jwt
import datetime
from models import User
from db import db  # 导入 db

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
@swag_from({
    'summary': '用户登录',
    'description': 'Login and obtain JWT token.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'user1'},
                    'password': {'type': 'string', 'example': 'password123'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'JWT token generated',
            'examples': {
                'application/json': {
                    'token': 'your_jwt_token_here'
                }
            }
        },
        401: {
            'description': 'Invalid credentials'
        }
    }
})
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"message": "Invalid credentials!"}), 401

    # 生成JWT token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")  # 使用 current_app

    user.token = token  # 储存生成的 token
    db.session.commit()

    return jsonify({"token": token}), 200

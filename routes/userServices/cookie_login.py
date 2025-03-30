from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import check_password_hash
from flasgger import swag_from
from datetime import datetime
from models import User, Session
from db import db

cookie_login_bp = Blueprint('cookie_login', __name__)

@cookie_login_bp.route('/user_services/cookie_login', methods=['POST'])
@swag_from({
    'summary': 'Cookie登录',
    'tags': ['用户认证服务'],
    'parameters': [{
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
    }],
    'responses': {
        200: {'description': '登录成功（响应头包含Set-Cookie）'},
        401: {'description': '认证失败'}
    }
})
def cookie_login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"message": "用户名或密码错误"}), 401

    # 先删除该用户所有现有会话
    Session.query.filter_by(user_id=user.id).delete()
    
    # 创建新会话
    new_session = Session(user=user)
    db.session.add(new_session)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "会话创建失败", "error": str(e)}), 500

    # 构建响应对象
    response = make_response(jsonify({
        "message": "登录成功",
        "nickname": user.nickname
    }))
    
    # 设置HTTP-only Cookie
    response.set_cookie(
        key='session_token',
        value=new_session.session_token,
        expires=new_session.token_expiry,
        httponly=True,
        secure=True,  # 测试环境建议设为False
        samesite='Lax',  # 建议测试时改为'None'
        path='/',       # 明确指定路径范围
        domain=None     # 确保与JMeter请求的域名匹配
    )

    return response
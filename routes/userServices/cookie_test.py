from datetime import datetime  # 添加datetime导入
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from models import Session, User

cookie_test_bp = Blueprint('cookie_test', __name__)

@cookie_test_bp.route('/user_services/cookie_test', methods=['GET'])
@swag_from({
    'summary': 'Cookie验证测试接口',
    'tags': ['测试服务'],
    'parameters': [{
        'name': 'Cookie',
        'in': 'header',
        'required': True,
        'description': '包含session_token的Cookie',
        'type': 'string'
    }],
    'responses': {
        200: {
            'description': '验证成功',
            'examples': {
                'application/json': {
                    "user_id": 123,
                    "username": "test_user",
                    "is_logged_in": True
                }
            }
        },
        401: {'description': '无效的会话令牌'}
    }
})
def cookie_test():
    """用于JMeter测试的Cookie验证接口"""
    current_time = datetime.utcnow()  # 现在可以正确使用datetime
    print(f"[DEBUG] 当前时间：{current_time}")
    
    session_token = request.cookies.get('session_token')
    print(f"[DEBUG] 收到会话令牌：{session_token}")
    
    if not session_token:
        return jsonify({"error": "缺少会话令牌"}), 401
    
    session = Session.query.filter_by(session_token=session_token).first()
    if not session:
        print("[DEBUG] 未找到对应会话记录")
        return jsonify({"error": "会话已过期"}), 401
    
    print(f"[DEBUG] 会话过期时间：{session.token_expiry}")
    print(f"[DEBUG] 时间差：{session.token_expiry - current_time}")
    
    if session.token_expiry < current_time:
        return jsonify({"error": "会话已过期"}), 401
    
    user = User.query.get(session.user_id)
    if not user:
        print(f"[DEBUG] 未找到用户 ID：{session.user_id}")
        return jsonify({"error": "用户不存在"}), 404
        
    print(f"[DEBUG] 用户验证成功：{user.username}")
    return jsonify({
        "user_id": user.id,
        "username": user.username,
        "is_logged_in": True,
        "balance": user.balance
    })
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from models import db, User
from plugin.auth import extract_token

add_balance_bp = Blueprint('add_balance', __name__)

@add_balance_bp.route('/add_balance', methods=['POST'])
@swag_from({
    'summary': '增加用户余额',
    'tags': ['管理员权限服务'],
    'description': 'Recharge user account balance by admin.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Admin token'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer', 'example': 1, 'description': 'ID of the user to recharge'},
                    'amount': {'type': 'number', 'example': 100.0, 'description': 'Amount to recharge'}
                },
                'required': ['user_id', 'amount']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Balance added successfully'
        },
        400: {
            'description': 'Invalid token, user ID, or amount'
        },
        403: {
            'description': 'Unauthorized access'
        }
    }
})
def add_balance():
    # 获取管理员 token
    admin_token = extract_token(request)
    admin_user = User.query.filter_by(token=admin_token).first()

    # 检查是否是管理员
    if not admin_user or admin_user.role != 0:  # role == 0 表示管理员
        return jsonify({"error": "Unauthorized access"}), 403

    # 获取请求中的用户 ID 和充值金额
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')

    # 检查传入的用户 ID 是否有效
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 400

    # 检查充值金额是否大于 0
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    # 更新用户余额
    user.balance += amount
    db.session.commit()

    return jsonify({"message": "Balance added successfully"}), 200

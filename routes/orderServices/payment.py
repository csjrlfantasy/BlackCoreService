from flask import Blueprint, request, jsonify
from models import db, User, Order
from flasgger import swag_from

from plugin.auth import extract_token

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/pay', methods=['POST'])
@swag_from({
    'summary': '向一个订单发起支付',
    'description': 'Endpoint to pay for an order based on its ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'main_order_id': {'type': 'string'}
                },
                'required': ['main_order_id']
            }
        }
    ],
    'responses': {
        200: {'description': 'Payment successful'},
        400: {'description': 'Invalid token or insufficient balance'},
        404: {'description': 'Order not found'},
        500: {'description': 'Payment failed'}
    }
})
def pay():
    data = request.json
    main_order_id = data.get('main_order_id')
    print("=============",main_order_id)
    if not main_order_id:
        return jsonify({"error": "Main Order ID is required"}), 400

    token = extract_token(request)
    user = User.query.filter_by(token=token).first()

    if not user:
        return jsonify({"error": "Invalid token"}), 400

    # 获取所有子订单
    orders = Order.query.filter_by(main_order_id=main_order_id, user_id=user.id).all()

    if not orders:
        return jsonify({"error": "订单未找到"}), 404

    total_amount = sum(order.product_price * order.quantity for order in orders)

    if user.balance < total_amount:
        return jsonify({"error": "余额不足"}), 400

    try:
        # 手动管理事务，确保没有嵌套事务冲突
        with db.session.no_autoflush:  # 暂时不提交数据到数据库
            user.balance -= total_amount  # 扣除用户余额

            # 更新所有订单的支付状态为已支付
            for order in orders:
                order.payment_status = 1  # 设置支付状态为已支付

        # 手动刷新会话中的所有更改
        db.session.flush()

        # 提交事务
        db.session.commit()

        return jsonify({"message": "Payment successful", "main_order_id": main_order_id}), 200

    except Exception as e:
        db.session.rollback()  # 发生错误时回滚事务
        return jsonify({"error": "Payment failed", "details": str(e)}), 500

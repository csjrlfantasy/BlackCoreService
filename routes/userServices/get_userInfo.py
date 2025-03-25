from flask import Blueprint, request, jsonify
from models import db, User, Order, Cart, CartItem
from flasgger import swag_from
from plugin.auth import extract_token
import time
user_info_bp = Blueprint('user_info', __name__)

@user_info_bp.route('/user_services/user_info', methods=['GET'])
@swag_from({
    'summary': '获取用户信息',
    'tags': ['用户管理服务'],
    'description': 'Display user information, including balance, pending and completed orders, and active carts.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User token for authentication'
        }
    ],
    'responses': {
        200: {
            'description': 'User information retrieved successfully',
            'examples': {
                'application/json': {
                    'user_id': 1,
                    'balance': 100.0,
                    'pending_orders': [
                        {'order_id': 1, 'product_id': 2, 'quantity': 1, 'total_price': 100.0}
                    ],
                    'completed_orders': [
                        {'order_id': 2, 'product_id': 3, 'quantity': 2, 'total_price': 200.0}
                    ],
                    'active_cart': {
                        'cart_id': 1,
                        'items': [
                            {'product_id': 2, 'quantity': 1, 'price': 100.0}
                        ]
                    }
                }
            }
        },
        400: {'description': 'Invalid token'},
        404: {'description': 'User not found'}
    }
})
def get_user_info():
    token = extract_token(request)
    user = User.query.filter_by(token=token).first()

    if not user:
        return jsonify({"error": "Invalid token or user not found"}), 404

    # 获取待支付和已支付订单
    pending_orders = Order.query.filter_by(user_id=user.id, payment_status=0).all()
    # 修改后的查询语句（添加显式排序）
    completed_orders = Order.query.filter_by(
        user_id=user.id, 
        payment_status=1
    ).order_by(
        Order.created_at.desc()  # 确保按时间倒序排列
    ).limit(10).all()

    # 获取未生成订单的购物车
    active_cart = Cart.query.filter_by(user_id=user.id).first()

    response = {
        'user_id': user.id,
        "nickname": user.nickname,
        'balance': user.balance,
        'pending_orders': [
            {
                'order_id': order.id,
                'product_id': order.product_id,
                'quantity': order.quantity,
                'total_price': (order.product_price or 0) * order.quantity  # 避免 NoneType 错误
            } for order in pending_orders
        ],
        'completed_orders': [
            {
                'order_id': order.id,
                'product_id': order.product_id,
                'quantity': order.quantity,
                'total_price': (order.product_price or 0) * order.quantity  # 避免 NoneType 错误
            } for order in completed_orders
        ],
        'active_cart': {
            'cart_id': active_cart.id if active_cart else None,
            'items': [
                {
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'price': item.product_price
                } for item in active_cart.cart_items
            ] if active_cart else []
        }
    }
    time.sleep(0.3)
    return jsonify(response), 200

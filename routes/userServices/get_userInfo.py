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

    # 获取用户所有未生成订单的购物车，只显示最近的10个
    active_carts = Cart.query.filter_by(user_id=user.id).order_by(Cart.created_at.desc()).limit(10).all()

    from collections import defaultdict
    
    # 按main_order_id分组订单
    def group_orders(orders):
        grouped = defaultdict(list)
        for order in orders:
            grouped[order.main_order_id].append(order)
        return [
            {
                'main_order_id': main_id,
                'orders': [
                    {
                        'order_id': o.id,
                        'product_id': o.product_id,
                        'quantity': o.quantity,
                        'total_price': (o.product_price or 0) * o.quantity
                    } for o in order_list
                ]
            } for main_id, order_list in grouped.items()
        ]
    
    pending_orders_grouped = group_orders(pending_orders)
    completed_orders_grouped = group_orders(completed_orders)

    response = {
        'user_id': user.id,
        "nickname": user.nickname,
        'balance': user.balance,
        'pending_orders': pending_orders_grouped,
        'completed_orders': completed_orders_grouped,
        'active_cart': [
            {
                'cart_id': cart.id,
                'total_price': cart.total_price,
                'items': [
                    {
                        'product_id': item.product_id,
                        'product_name': item.product_name,
                        'quantity': item.quantity,
                        'price': float(item.product_price)
                    } for item in cart.cart_items
                ]
            } for cart in active_carts
        ]
    }
    time.sleep(0.3)
    return jsonify(response), 200

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from models import db, User, Product, Order, Cart
from plugin.auth import extract_token

create_order_bp = Blueprint('create_order', __name__)


@create_order_bp.route('/order', methods=['POST'])
@swag_from({
    'tags': ['订单管理'],
    'summary': '创建订单',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'cart_id': {'type': 'integer'}
                },
                'required': ['cart_id']
            }
        }
    ],
    'responses': {
        201: {'description': 'Order created successfully'},
        400: {'description': 'Invalid token, insufficient stock or balance'}
    }
})
def create_order():
    token = extract_token(request)
    user = User.query.filter_by(token=token).first()

    if not user:
        return jsonify({"error": "Invalid token"}), 400

    data = request.json
    cart_id = data.get('cart_id')

    # 获取购物车
    cart = Cart.query.get(cart_id)
    if not cart or cart.user_id != user.id:
        return jsonify({"error": "Invalid cart or user does not own this cart"}), 400

    try:
        total_amount = 0

        # 遍历购物车项目，计算总金额并创建订单项
        for cart_item in cart.cart_items:
            product = Product.query.get(cart_item.product_id)

            if not product or product.stock < cart_item.quantity:
                return jsonify({"error": f"Insufficient stock for product {product.id}"}), 400

            total_amount += product.price * cart_item.quantity

            # 减少库存
            product.stock -= cart_item.quantity

            # 创建订单项
            new_order = Order(product_id=product.id, user_id=user.id, quantity=cart_item.quantity,
                              product_price=product.price, main_order_id=f"main_{cart_id}")
            db.session.add(new_order)

        db.session.commit()  # 提交事务

        return jsonify({"message": "Order created successfully", "main_order_id": f"main_{cart_id}"}), 201

    except Exception as e:
        db.session.rollback()  # 回滚事务
        return jsonify({"error": "Failed to create order", "details": str(e)}), 500

from flask import Blueprint, request, jsonify
from models import db, User, Product, Cart, CartItem
from datetime import datetime
from flasgger import swag_from

from plugin.auth import extract_token

add_to_cart_bp = Blueprint('add_to_cart', __name__)


@add_to_cart_bp.route('/add_to_cart', methods=['POST'])
@swag_from({
    'summary': '添加到购物车',
    'tags': ['购物车管理服务'],
    'description': 'Add multiple products to the cart and calculate total price.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User token for authentication'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'items': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product_id': {'type': 'integer'},
                                'quantity': {'type': 'integer'}
                            },
                            'required': ['product_id', 'quantity']
                        }
                    }
                },
                'required': ['items']
            }
        }
    ],
    'responses': {
        201: {'description': 'Items added to cart successfully'},
        400: {'description': 'Invalid request or product not found'}
    }
})
def add_to_cart():
    token = extract_token(request)
    print("token是===============",token)
    try:
        # user = User.query.filter_by(token=token).first()
        user = get_user_with_retries(token)

        print(user)
        if not user:
            return jsonify({"error": "~~~~Invalid token"}), 400
    except Exception as e:
        # 捕获其他异常
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500

    data = request.json
    items = data.get('items', [])

    if not items:
        return jsonify({"error": "No items to add"}), 400

    total_price = 0.0
    cart = Cart(user_id=user.id, total_price=0.0)
    db.session.add(cart)
    db.session.flush()  # 获取生成的购物车ID

    for item in items:
        product = Product.query.get(item['product_id'])
        if not product:
            return jsonify({"error": f"Product with ID {item['product_id']} not found"}), 400

        quantity = item['quantity']
        product_price = product.price * quantity
        total_price += product_price

        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            quantity=quantity
        )
        db.session.add(cart_item)

    # 更新购物车总价
    cart.total_price = total_price
    db.session.commit()

    # 返回购物车信息
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    cart_items_info = [
        {
            "product_id": item.product_id,
            "product_name": item.product_name,
            "product_price": item.product_price,
            "quantity": item.quantity
        }
        for item in cart_items
    ]

    return jsonify({
        "cart_id": cart.id,
        "total_price": total_price,
        "items": cart_items_info
    }), 201


import time

def get_user_with_retries(token, retries=3, delay=0.1):
    for attempt in range(retries):
        user = User.query.filter_by(token=token).first()
        if user:
            return user
        time.sleep(delay)  # 等待后重试
    return None


from flask import Blueprint, request, jsonify
from flasgger import swag_from
from models import db,User, Product, Order, FlashSaleOrder
from plugin.stock_checker import check_product_stock
from datetime import datetime
import requests


flash_sale_bp = Blueprint('flash_sale', __name__)

@flash_sale_bp.route('/flash_sale', methods=['POST'])
@swag_from({
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
                    'product_id': {'type': 'integer'},
                    'quantity': {'type': 'integer'}
                },
                'required': ['product_id', 'quantity']
            }
        }
    ],
    'responses': {
        201: {'description': 'Order created successfully'},
        400: {'description': 'Insufficient stock or balance'},
        503: {'description': 'Service unavailable'}
    }
})
def flash_sale():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()

    if not user:
        return jsonify({"error": "Invalid token"}), 400

    data = request.json
    product = Product.query.get(data['product_id'])

    if not product:
        return jsonify({"error": "Product not found"}), 404

    total_amount = product.price * data['quantity']

    if user.balance < total_amount:
        return jsonify({"error": "Insufficient balance"}), 400

    # 检查库存
    if not check_product_stock(data['product_id'], data['quantity']):
        return jsonify({"error": "Insufficient stock"}), 400

    # 调用外部服务进行处理
    external_service_url = "http://localhost:5001/validate_order"
    response = requests.get(external_service_url)

    if response.status_code != 200:
        return jsonify({"error": "External service error", "details": response.json()}), 503

    response_data = response.json()
    if not response_data.get("valid", False):
        return jsonify({"error": "Order is invalid"}), 400

    # 扣除余额和更新库存
    try:
        with db.session.begin_nested():
            user.balance -= total_amount
            product.stock -= data['quantity']
            new_order = Order(product_id=product.id, user_id=user.id, quantity=data['quantity'])
            db.session.add(new_order)

            # 记录秒杀订单
            flash_sale_order = FlashSaleOrder(
                product_id=product.id,
                user_id=user.id,
                amount=total_amount,
                purchase_time=datetime.utcnow()
            )
            db.session.add(flash_sale_order)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    return jsonify({"message": "Order created successfully"}), 201  # 确保在成功时返回响应
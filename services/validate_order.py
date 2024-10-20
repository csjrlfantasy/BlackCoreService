from flask import Blueprint, request, jsonify
from models import User, Product

validate_order_bp = Blueprint('validate_order', __name__)

@validate_order_bp.route('/validate_order', methods=['POST'])
def validate_order():
    data = request.json
    token = data.get('token')
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    user = User.query.filter_by(token=token).first()
    product = Product.query.get(product_id)

    if not user:
        return jsonify({"valid": False, "error": "Invalid token"}), 400

    if not product or product.stock < quantity:
        return jsonify({"valid": False, "error": "Insufficient stock"}), 400

    total_amount = product.price * quantity

    if user.balance < total_amount:
        return jsonify({"valid": False, "error": "Insufficient balance"}), 400

    return jsonify({"valid": True}), 200
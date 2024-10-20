# update_product_stock.py

from flask import Blueprint, request, jsonify
from models import db, Product
from flasgger import swag_from
from plugin.auth import check_admin_role  # 引入权限检查模块

update_product_stock_bp = Blueprint('update_product_stock', __name__)

@update_product_stock_bp.route('/update_product_stock/<int:product_id>', methods=['PUT'])
@swag_from({
    'summary': 'Update product stock',
    'description': 'This endpoint updates the stock of a product by its ID. Admin token is required.',
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the product to update the stock for'
        },
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Admin token required for authorization'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'stock': {
                        'type': 'integer',
                        'example': 50,
                        'description': 'The new stock value for the product'
                    }
                },
                'required': ['stock']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Product stock updated successfully',
            'examples': {
                'application/json': {
                    'message': 'Product stock updated successfully'
                }
            }
        },
        404: {
            'description': 'Product not found',
            'examples': {
                'application/json': {
                    'error': 'Product not found'
                }
            }
        },
        500: {
            'description': 'Failed to update product stock',
            'examples': {
                'application/json': {
                    'error': 'Failed to update product stock',
                    'details': 'Error details here'
                }
            }
        }
    }
})
def update_product_stock(product_id):
    # 从请求头中获取token并检查管理员权限
    token = request.headers.get('Authorization')
    admin_check = check_admin_role(token)
    if admin_check:
        return admin_check  # 如果权限不通过，直接返回相应的错误

    # 查找商品
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.json
    new_stock = data.get('stock')

    if new_stock is None or new_stock < 0:
        return jsonify({"error": "Invalid stock value"}), 400

    try:
        product.stock = new_stock
        db.session.commit()
        return jsonify({"message": "Product stock updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update product stock", "details": str(e)}), 500

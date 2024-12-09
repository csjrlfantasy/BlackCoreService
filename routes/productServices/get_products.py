from flask import Blueprint, jsonify, request, make_response
from flasgger import swag_from
from models import Product
import time
from db import db

get_products_bp = Blueprint('get_products', __name__)

@get_products_bp.route('/product_services/products', methods=['GET'])
@swag_from({
    'summary': '查询商品种类',
    'tags': ['商品管理服务'],
    'description': 'Retrieve all products or a specific product by ID.',
    'parameters': [
        {
            'name': 'id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Product ID to retrieve a specific product.'
        }
    ],
    'responses': {
        200: {
            'description': 'List of products or a specific product.',
            'examples': {
                'application/json': {
                    'products': [
                        {
                            'id': 1,
                            'name': 'Product 1',
                            'price': 10.0,
                            'stock': 100
                        },
                        {
                            'id': 2,
                            'name': 'Product 2',
                            'price': 15.0,
                            'stock': 50
                        }
                    ]
                }
            }
        },
        404: {
            'description': '商品未找到'
        }
    }
})
def get_products():
    product_id = request.args.get('id')  # 获取查询参数中的 id
    print("获取到的id",product_id)
    if product_id:
        product = Product.query.filter_by(id=product_id).first()
        if product:
            return jsonify({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'stock': product.stock
            }), 200
        else:
            return jsonify({"message": "商品未找到"}), 404
    else:
        products = Product.query.all()
        response= make_response(jsonify([{
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'stock': product.stock
        } for product in products]), 200)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        time.sleep(0.1)
        return response

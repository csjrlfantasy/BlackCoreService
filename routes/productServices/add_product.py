from flask import Blueprint, request, jsonify
from models import Product
from db import db
from flasgger import swag_from

add_product_bp = Blueprint('add_product', __name__)


@add_product_bp.route('/add_product', methods=['POST'])
@swag_from({
    'summary': '增加商品种类',
    'tags': ['商品管理服务'],
    'description': 'Add a new product to the inventory.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'New Product'},
                    'price': {'type': 'number', 'example': 15.99},
                    'stock': {'type': 'integer', 'example': 100}
                },
                'required': ['name', 'price', 'stock']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Product added successfully',
            'examples': {
                'application/json': {
                    'message': 'Product added successfully!'
                }
            }
        },
        400: {
            'description': 'Error adding product'
        }
    }
})
def add_product():
    data = request.json

    new_product = Product(
        name=data['name'],
        price=data['price'],
        stock=data['stock']
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({"message": "Product added successfully!"}), 201

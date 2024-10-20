from flask import Blueprint, request, jsonify
from models import db, Product
from flasgger import swag_from

delete_product_bp = Blueprint('delete_product', __name__)

@delete_product_bp.route('/delete_product/<int:product_id>', methods=['DELETE'])
@swag_from({
    'summary': 'Delete a product',
    'description': 'This endpoint deletes a product by its ID.',
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The ID of the product to be deleted'
        }
    ],
    'responses': {
        200: {
            'description': 'Product deleted successfully',
            'examples': {
                'application/json': {
                    'message': 'Product deleted successfully'
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
            'description': 'Failed to delete product',
            'examples': {
                'application/json': {
                    'error': 'Failed to delete product',
                    'details': 'Error details here'
                }
            }
        }
    }
})
def delete_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete product", "details": str(e)}), 500

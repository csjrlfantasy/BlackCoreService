from flask import Blueprint, jsonify, request
from plugin.auth import extract_token
from models import db, User, Order, Cart, CartItem, GetOrder, Product
from plugin.response import success, error
from flasgger import swag_from

get_order_bp = Blueprint('get_order', __name__)

@get_order_bp.route('/api/v1/get_order/<string:main_order_id>', methods=['GET'])
@swag_from({
    'tags': ['订单管理'],
    'summary': '查询订单详情',
    'parameters': [
        {
            'name': 'main_order_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '主订单号'
        },
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': '登录token'
        }
    ],
    'responses': {
        200: {
            'description': '成功',
            'schema': {
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'msg': {'type': 'string', 'example': '成功'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'main_order_id': {'type': 'string'},
                            'total_amount': {'type': 'number'},
                            'user': {
                                'type': 'object',
                                'properties': {
                                    'user_id': {'type': 'integer'},
                                    'username': {'type': 'string'}
                                }
                            },
                            'products': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'product_id': {'type': 'integer'},
                                        'name': {'type': 'string'},
                                        'price': {'type': 'number'}
                                    }
                                }
                            },
                            'create_time': {'type': 'string'},
                            'update_time': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
})
def get_order_detail(main_order_id):
    token = extract_token(request)
    user = User.query.filter_by(token=token).first()

    if not user:
        return jsonify({"error": "Invalid token or user not found"}), 404
    try:
        order_service = OrderService()
        order_data = order_service.get_order_detail(main_order_id)
        
        if not order_data:
            return error(msg='订单不存在')
            
        return success(data=order_data)
    except Exception as e:
        return error(msg=str(e))
    

    # ... existing code ...

class OrderService:
    def get_order_detail(self, main_order_id):
        """获取订单详情"""
        # 查询订单基本信息
        order = Order.query.filter_by(main_order_id=main_order_id).first()
        if not order:
            return None
        
        # 查询订单关联的用户信息
        user = User.query.get(order.user_id)
        
        # 查询订单商品信息
        order_items = Order.query.filter_by(main_order_id=main_order_id).all()
        
        # 构建商品列表并计算总金额
        products = []
        total_amount = 0
        for item in order_items:
            product = Product.query.get(item.product_id)
            if product:
                subtotal = float(item.product_price * item.quantity)
                total_amount += subtotal
                product_info = {
                    'product_id': item.product_id,
                    'name': product.name,
                    'price': float(item.product_price),
                    'quantity': item.quantity,
                    'subtotal': subtotal
                }
                products.append(product_info)
        
        # 构建返回数据
        order_data = {
            'main_order_id': order.main_order_id,
            'total_amount': total_amount,  # 使用计算得到的总金额
            'user': {
                'user_id': user.id,
                'username': user.username
            },
            'products': products,
            'create_time': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status': order.status
        }
        
        return order_data
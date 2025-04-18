from flask import Blueprint, jsonify, request, make_response
from flasgger import swag_from
from models import Product
import time
from db import db
from utils.redis_util import redis_client  # 从工具类导入
from math import ceil

# 删除所有Redis初始化相关代码，直接使用导入的redis_client

get_products_bp = Blueprint('get_products', __name__)

@get_products_bp.route('/product_services/products', methods=['GET'])
@swag_from({
    'summary': '查询商品种类',
    'tags': ['商品管理服务'],
    'description': '查询单个商品或分页查询商品列表',
    'parameters': [
        {
            'name': 'id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': '商品ID，查询单个商品时使用'
        },
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 10,
            'description': '每页商品数量，最大100'
        },
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 1,
            'description': '页码，从1开始'
        }
    ],
    'responses': {
        200: {
            'description': '查询成功',
            'examples': {
                '单个商品': {
                    'id': 1,
                    'name': '商品1',
                    'price': 10.0,
                    'stock': 100
                },
                '分页商品': {
                    'products': [
                        {
                            'id': 1,
                            'name': '商品1',
                            'price': 10.0,
                            'stock': 100
                        },
                        {
                            'id': 2,
                            'name': '商品2',
                            'price': 15.0,
                            'stock': 50
                        }
                    ],
                    'total_pages': 5,
                    'current_page': 1
                }
            }
        },
        400: {
            'description': '参数错误',
            'examples': {
                'application/json': {
                    'error': '缺少必要参数'
                }
            }
        },
        404: {
            'description': '商品未找到'
        },
        500: {
            'description': '服务器内部错误'
        }
    }
})
def get_products():
    product_id = request.args.get('id')
    limit = min(int(request.args.get('limit', 10)), 100)
    page = int(request.args.get('page', 1))
    offset = (page - 1) * limit
    start_time = time.time()  # 将start_time定义移到函数开头
    
    print(f"分页参数 - limit: {limit}, page: {page}, offset: {offset}")

    if product_id:
        # 修改为完整的降级处理
        if not redis_client:
            print("缓存不可用，直接查询数据库")
            product = Product.query.filter_by(id=product_id).first()
            if product:
                product_data = {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'stock': product.stock
                }
                time.sleep(3) # 模拟耗时
                elapsed_time = time.time() - start_time
                print(f"降级查询单个商品耗时: {elapsed_time} 秒")
                return jsonify(product_data), 200
            else:
                elapsed_time = time.time() - start_time
                print(f"降级查询未找到商品耗时: {elapsed_time} 秒")
                return jsonify({"message": "商品未找到"}), 404
        # 构建缓存键
        cache_key = 'all_products'
        try:
            # 尝试从 Redis 缓存中获取数据
            cached_products = redis_client.get(cache_key)
        except redis.exceptions.ConnectionError as e:
            print(f"Redis 连接错误: {e}")
            return jsonify({"message": "Redis 连接错误，请稍后重试"}), 500
        if cached_products:
            # 如果缓存存在，直接返回缓存数据
            elapsed_time = time.time() - start_time  # 计算耗时
            print(f"使用缓存查询所有商品耗时: {elapsed_time} 秒")
            return jsonify(eval(cached_products.decode())), 200
        else:
            time.sleep(3)  # 模拟数据库查询耗时
            products = Product.query.all()
            response_data = [
                {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'stock': product.stock
                } for product in products
            ]
            try:
                # 将数据存入 Redis 缓存
                redis_client.set(cache_key, str(response_data))
            except redis.exceptions.ConnectionError as e:
                print(f"Redis 连接错误: {e}")
                return jsonify({"message": "Redis 连接错误，数据未缓存"}), 500
            response = make_response(jsonify(response_data), 200)
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            elapsed_time = time.time() - start_time  # 计算耗时
            print(f"未使用缓存查询所有商品耗时: {elapsed_time} 秒")
            return response
    else:
        # 添加完整的降级处理并返回响应
        if not redis_client:
            print("缓存不可用，直接查询数据库")
            time.sleep(3)  # 保持与缓存逻辑一致的模拟耗时
            products = Product.query.offset(offset).limit(limit).all()
            total = Product.query.count()
            response_data = {
                'products': [{
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'stock': product.stock
                } for product in products],
                'total_pages': ceil(total / limit),
                'current_page': page
            }
            elapsed_time = time.time() - start_time
            print(f"降级分页查询耗时: {elapsed_time} 秒")
            return jsonify(response_data), 200
        
        # 以下是正常的缓存处理流程
        cache_key = f'products_page_{page}_limit_{limit}'
        try:
            cached_products = redis_client.get(cache_key)
        except redis.exceptions.ConnectionError as e:
            print(f"Redis 连接错误: {e}")
            return jsonify({"message": "Redis 连接错误，请稍后重试"}), 500

        if cached_products:
            # 如果缓存存在，直接返回缓存数据
            elapsed_time = time.time() - start_time
            print(f"使用缓存分页查询耗时: {elapsed_time} 秒")
            return jsonify(eval(cached_products.decode())), 200
        else:
            time.sleep(3)
            products = Product.query.offset(offset).limit(limit).all()
            total = Product.query.count()
            response_data = {
                'products': [{
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'stock': product.stock
                } for product in products],
                'total_pages': ceil(total / limit),
                'current_page': page
            }
            try:
                redis_client.setex(cache_key, 60, str(response_data))  # 缓存60秒
            except redis.exceptions.ConnectionError as e:
                print(f"Redis 连接错误: {e}")
                return jsonify({"message": "Redis 连接错误，数据未缓存"}), 500
            elapsed_time = time.time() - start_time
            print(f"未使用缓存分页查询耗时: {elapsed_time} 秒")
            return jsonify(response_data)

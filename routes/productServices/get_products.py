from flask import Blueprint, jsonify, request, make_response
from flasgger import swag_from
from models import Product
import time
from db import db
import redis

# 修改 Redis 连接部分（第8-19行）
try:
    # 连接到 Redis
    redis_client = redis.Redis(
        host='192.168.11.119',
        port=6379,
        db=0,
        socket_connect_timeout=3  # 添加超时设置
    )
    # 测试 Redis 连接
    redis_client.ping()
    print("成功连接到 Redis 服务器")
except Exception as e:  # 捕获所有异常类型
    print(f"Redis 连接异常: {e}")
    redis_client = None  # 确保客户端设为None
    import logging
    logging.error(f"Redis 初始化失败: {e}，缓存功能不可用")
    # 移除 sys.exit(1) 保持服务运行

# 在路由函数中修改容错逻辑（删除503返回）
# 修复代码顺序问题（蓝图对象需要先定义）
get_products_bp = Blueprint('get_products', __name__)  # 将此行移到路由装饰器之前

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
def get_products():  # 确保路由装饰器在函数定义上方
    product_id = request.args.get('id')  # 获取查询参数中的 id
    print("获取到的id", product_id)

    start_time = time.time()  # 记录开始时间

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
            products = Product.query.all()
            response_data = [{
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'stock': product.stock
            } for product in products]
            elapsed_time = time.time() - start_time
            print(f"降级查询所有商品耗时: {elapsed_time} 秒")
            return jsonify(response_data), 200  # 添加返回语句
        
        # 以下是正常的缓存处理流程
        cache_key = 'all_products'
        try:
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

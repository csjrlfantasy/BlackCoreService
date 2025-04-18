from flask import Blueprint, request, jsonify
from flasgger import swag_from
from models import db, User, Product, Order, FlashSaleOrder
from plugin.auth import extract_token
from plugin.stock_checker import check_product_stock
from datetime import datetime
import time
import requests
import pika
import threading  # 添加这行导入
from threading import Lock
from config import RABBITMQ_CONFIG
import json  # 导入json模块
from sqlalchemy.exc import DatabaseError, IntegrityError

flash_sale_bp = Blueprint('flash_sale', __name__)

# 添加消费者处理函数
def process_flash_sale():
    if rabbitmq_channel is None:
        print("RabbitMQ不可用，消费者线程终止")
        return

    def flash_sale_callback(ch, method, properties, body):
        from app import create_app  # 导入create_app函数
        app = create_app()  # 创建应用实例
        
        with app.app_context():  # 添加应用上下文
            try:
                data = json.loads(body)
                user_id = data['user_id']
                product_id = data['product_id']
                quantity = data['quantity']

                try:
                    # 在直接处理逻辑中添加
                    with order_lock:
                        product = db.session.query(Product).filter_by(id=product_id).with_for_update().first()
                        user = db.session.query(User).filter_by(id=user_id).with_for_update().first()

                        if not user or not product:
                            ch.basic_nack(delivery_tag=method.delivery_tag)
                            return

                        total_amount = product.price * quantity

                        # 双重检查库存和余额
                        if user.balance < total_amount or product.stock < quantity:
                            ch.basic_nack(delivery_tag=method.delivery_tag)
                            return

                        # 执行订单创建
                        try:
                            user.balance -= total_amount
                            product.stock -= quantity
                            new_order = Order(product_id=product.id, user_id=user.id, quantity=quantity)
                            db.session.add(new_order)

                            flash_sale_order = FlashSaleOrder(
                                product_id=product.id,
                                user_id=user.id,
                                amount=total_amount,
                                purchase_time=datetime.utcnow()
                            )
                            db.session.add(flash_sale_order)

                            db.session.commit()
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            print(f"成功创建订单，剩余库存: {product.stock}")
                        except Exception as e:
                            db.session.rollback()
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                            print(f"订单创建失败: {e}")

                except Exception as e:
                    db.session.rollback()
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    print(f"处理消息时发生错误: {e}")
            except Exception as e:  # 添加最外层异常捕获
                db.session.rollback()
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                print(f"消息解析失败: {e}")

    # 启动消费者
    try:
        rabbitmq_channel.basic_qos(prefetch_count=1)  # 每次只处理一个消息
        rabbitmq_channel.basic_consume(
            queue='flash_sale_queue',
            on_message_callback=flash_sale_callback,  # 修改为新的回调函数名
            auto_ack=False
        )
        print("开始消费消息队列...")
        rabbitmq_channel.start_consuming()
    except Exception as e:
        print(f"RabbitMQ消费错误: {e}")


# 修改RabbitMQ初始化逻辑
def init_rabbitmq():
    try:
        credentials = pika.PlainCredentials(
            RABBITMQ_CONFIG['USERNAME'],
            RABBITMQ_CONFIG['PASSWORD']
        )
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_CONFIG['HOST'],
            port=RABBITMQ_CONFIG['PORT'],
            virtual_host=RABBITMQ_CONFIG['VIRTUAL_HOST'],
            credentials=credentials,
            heartbeat=RABBITMQ_CONFIG['HEARTBEAT'],
            blocked_connection_timeout=RABBITMQ_CONFIG['BLOCKED_CONNECTION_TIMEOUT'],
            # Add these new parameters
            connection_attempts=3,  # Retry connection 3 times
            retry_delay=5,  # Wait 5 seconds between retries
            socket_timeout=10,  # Socket operation timeout
            stack_timeout=10,  # Protocol negotiation timeout
            frame_max=131072  # Increase max frame size to prevent frame_too_large errors
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(
            queue=RABBITMQ_CONFIG['QUEUE_NAME'],
            durable=True
        )
        return channel
    except Exception as e:
        print(f"RabbitMQ连接失败: {e}, 将使用直接处理模式")
        return None


rabbitmq_channel = init_rabbitmq()
order_lock = Lock()


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
    global rabbitmq_channel  # 添加这行声明全局变量
    time.sleep(0.5)
    token = extract_token(request)

    user = User.query.filter_by(token=token).first()

    if not user:
        return jsonify({"error": "Invalid token"}), 400

    data = request.json
    product_id = data['product_id']
    quantity = data['quantity']

    # 基础验证
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # 将请求放入消息队列
    if rabbitmq_channel:
        for attempt in range(3):  # Retry up to 3 times
            try:
                # 检查通道是否关闭，如果是则重新连接
                if rabbitmq_channel.is_closed:
                    rabbitmq_channel = init_rabbitmq()
                    
                rabbitmq_channel.basic_publish(
                    exchange='',
                    routing_key='flash_sale_queue',
                    body=json.dumps({
                        'user_id': user.id,
                        'product_id': product_id,
                        'quantity': quantity,
                        'total_amount': product.price * quantity,
                    }),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                    )
                )
                return jsonify({"message": "Request received, processing..."}), 202
            except (pika.exceptions.AMQPConnectionError, 
                   pika.exceptions.StreamLostError) as e:
                print(f"RabbitMQ连接失败 (尝试 {attempt+1}/3): {e}")
                if attempt < 2:  # Not last attempt
                    time.sleep(1)  # Wait before retry
                    rabbitmq_channel = init_rabbitmq()  # Reconnect
                    continue
                print("RabbitMQ重试失败，将使用直接处理模式")
                rabbitmq_channel = None
                break
            except Exception as e:
                print(f"RabbitMQ发布失败: {e}, 将使用直接处理模式")
                rabbitmq_channel = None
                break
    
    # RabbitMQ不可用时的直接处理逻辑
    try:
        with order_lock:
            user = User.query.get(user.id)
            product = Product.query.get(product_id)

            if not user or not product:
                return jsonify({"error": "Invalid user or product"}), 400

            # 封装计算 total_amount 的函数
            def calculate_total_amount(product, quantity):
                # 示例实现，根据实际情况修改
                return product.price * quantity
           
            total_amount = calculate_total_amount(product, quantity)

            if user.balance < total_amount or product.stock < quantity:
                return jsonify({
                    "status": "failed",
                    "reason": "Insufficient stock or balance"
                }), 200  # 修改为返回200状态码

            # 执行订单创建
            with db.session.begin_nested():
                user.balance -= total_amount
                product.stock -= quantity
                new_order = Order(product_id=product.id, user_id=user.id, quantity=quantity)
                db.session.add(new_order)
                flash_sale_order = FlashSaleOrder(
                    product_id=product.id,
                    user_id=user.id,
                    amount=total_amount,
                    purchase_time=datetime.utcnow()
                )
                db.session.add(flash_sale_order)
            db.session.commit()
            return jsonify({"message": "Order created successfully"}), 201

    except (DatabaseError, IntegrityError, Exception) as e:  # 合并异常捕获
        db.session.rollback()
        return jsonify({"error": "Order processing failed", "details": str(e)}), 500

# 修改消费者线程启动逻辑
if rabbitmq_channel is not None:
    consumer_thread = threading.Thread(target=process_flash_sale, daemon=True)
    consumer_thread.start()
    print("RabbitMQ消费者线程已启动")
else:
    print("RabbitMQ不可用，跳过消费者线程启动")
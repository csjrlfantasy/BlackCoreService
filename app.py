import pika
from flasgger import Swagger
from flask import Flask
from db import db  # 导入 db
from routes.userServices.register import register_bp
from routes.userServices.login import login_bp
from routes.productServices.add_product import add_product_bp
from routes.orderServices.create_order import create_order_bp
from routes.orderServices.payment import payment_bp
from routes.adminServices.add_balance import add_balance_bp
from routes.productServices.get_products import get_products_bp
from routes.flashSale.flash_sale import flash_sale_bp
from routes.productServices.delete_product import delete_product_bp
from routes.productServices.update_product_stock import update_product_stock_bp
from routes.cartServices.add_to_cart import add_to_cart_bp
from routes.userServices.get_userInfo import user_info_bp
from routes.signServices.agreement_sign import agreement_sign_bp
from routes.orderServices.get_order import get_order_bp
from routes.productServices.generate_sign import generate_sign  # noqa: F401
from routes.productServices.file_handling import file_bp
from routes.userServices.cookie_login import cookie_login_bp
from routes.userServices.cookie_test import cookie_test_bp
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY, RABBITMQ_CONFIG  # 导入 RABBITMQ_CONFIG
import threading
from tcp_server import start_tcp_server
import json
from models import User, Product, Order, FlashSaleOrder
import datetime
from models import Product  # 假设 Product 模型定义在 models.py 中

def create_app():
    app = Flask(__name__)
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': SQLALCHEMY_DATABASE_URI,
        'SQLALCHEMY_TRACK_MODIFICATIONS': SQLALCHEMY_TRACK_MODIFICATIONS,
        'SECRET_KEY': SECRET_KEY
    })

    # 配置Flasgger的Swagger相关设置，修改这里的title等属性来改变顶部文字
    app.config['SWAGGER'] = {
        'title': '黑核商城接口文档',  # 修改为你想要的标题，这个会显示在Swagger UI顶部
        'uiversion': 3,  # 可以指定Swagger UI的版本，这里示例设为3
        'description': '这里是关于本接口文档的详细描述内容，可以介绍接口功能、使用场景等信息',
        'termsOfService': "",  # 服务条款相关链接，可按需填写
        'contact': {
            'name': '联系人姓名（可选）',
            'url': '联系人网址（可选）',
            'email': '联系人邮箱（可选）'
        },
        'license': {
            'name': '许可证名称（可选）',
            'url': '许可证相关网址（可选）'
        }
    }

    db.init_app(app)  # 初始化应用
    # 注册蓝图
    app.register_blueprint(add_balance_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(create_order_bp)
    app.register_blueprint(add_product_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(get_products_bp)
    app.register_blueprint(flash_sale_bp)
    app.register_blueprint(delete_product_bp)
    app.register_blueprint(update_product_stock_bp)
    app.register_blueprint(add_to_cart_bp)
    app.register_blueprint(user_info_bp)
    app.register_blueprint(agreement_sign_bp)
    app.register_blueprint(get_order_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(cookie_login_bp)
    app.register_blueprint(cookie_test_bp)

    swagger = Swagger(app)
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()

    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()

    app.run(debug=True, host='0.0.0.0', port=5000)

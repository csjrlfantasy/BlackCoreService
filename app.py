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


# 其他导入...

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:heihe123456@localhost/heihe_mall'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

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

swagger = Swagger(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建数据库表
    app.run(debug=True, host='0.0.0.0', port=5000)
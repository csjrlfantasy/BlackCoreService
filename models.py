import string
from db import db  # 从 db 导入已初始化的 db 实例
from datetime import datetime
import random

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(120), unique=True, nullable=True)
    balance = db.Column(db.Float, default=0.0)
    role = db.Column(db.Integer, default=1)
    nickname = db.Column(db.String(120), nullable=False)

    # 添加这个关系定义
    get_order = db.relationship(
        "GetOrder",
        overlaps="orders,user,get_orders"
    )

    def generate_default_nickname(self):
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        return f"用户{random_str}"

class Order(db.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.Integer, default=0)  # 0: 未支付, 1: 已支付
    main_order_id = db.Column(db.String(50), nullable=True)
    product_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 添加 status 列

    # 关系定义
    product = db.relationship('Product', backref='orders')
    user = db.relationship("User", backref=db.backref("orders", lazy="dynamic"))
    
    def to_dict(self):
        return {
            'id': self.id,
            'main_order_id': self.main_order_id,
            'status': self.status,  # 添加 status 到返回数据中
            'user': {
                'user_id': self.user.id,
                'username': self.user.username
            },
            'product': {
                'product_id': self.product.id,
                'name': self.product.name,
                'price': float(self.product_price),
                'quantity': self.quantity
            },
            'payment_status': self.payment_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class FlashSaleOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    purchase_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='flash_sale_orders')
    product = db.relationship('Product', backref='flash_sale_orders')

class DiscountConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    min_amount = db.Column(db.Float, nullable=False)  # 最小金额区间
    max_amount = db.Column(db.Float, nullable=False)  # 最大金额区间
    discount_rate = db.Column(db.Float, nullable=False)  # 折扣率，范围0-1

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    cart_items = db.relationship('CartItem', backref='cart', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    product_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# 修改订单-产品的中间表定义
order_products = db.Table('order_products',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('quantity', db.Integer, nullable=False),
    db.Column('price', db.Numeric(10, 2), nullable=False)
)


class GetOrder(db.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'order'
    
    id = db.Column(db.Integer, primary_key=True)
    main_order_id = db.Column(db.String(32), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 修改为 'user.id'
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 添加状态字段
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 修改关联关系定义
    products = db.relationship(
        'Product',
        secondary=order_products,
        primaryjoin=(id == order_products.c.order_id),
        secondaryjoin=(Product.id == order_products.c.product_id),
        backref=db.backref('get_orders', lazy='dynamic')
    )
    
    # 修改与User的关系定义
    user = db.relationship(
        "User",
        backref=db.backref(
            "get_orders", 
            lazy="dynamic",
            overlaps="get_order,orders,user"  # 更新 overlaps 参数
        ),
        overlaps="get_order,orders,user"  # 更新 overlaps 参数
    )

    
    def to_dict(self):
        return {
            'main_order_id': self.main_order_id,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'user': {
                'user_id': self.user.id,
                'username': self.user.username
            },
            'products': [{
                'product_id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': self.get_product_quantity(product.id)  # 添加数量信息
            } for product in self.products],
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_product_quantity(self, product_id):
        """获取订单中特定产品的数量"""
        result = db.session.query(order_products.c.quantity).filter(
            order_products.c.order_id == self.id,
            order_products.c.product_id == product_id
        ).first()
        return result[0] if result else 0
from models import Product

def check_product_stock(product_id, quantity):
    """检查产品库存，返回布尔值"""
    product = Product.query.get(product_id)
    if not product:
        return False  # 产品不存在

    return product.stock >= quantity  # 返回是否有足够的库存
from models import db, DiscountConfig

def calculate_discount(total_amount):
    # 查询符合条件的折扣区间
    discount_config = DiscountConfig.query.filter(
        DiscountConfig.min_amount <= total_amount,
        DiscountConfig.max_amount > total_amount
    ).first()

    if discount_config:
        # 获取对应的折扣率
        discount_rate = discount_config.discount_rate
        discounted_amount = total_amount * discount_rate
        return discounted_amount, discount_rate
    else:
        # 默认不打折
        return total_amount, 1.0

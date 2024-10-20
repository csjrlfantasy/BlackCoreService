from db import get_db_session
from models import DiscountConfig

def calculate_discounted_price(amount):
    session = next(get_db_session())
    discount_configs = session.query(DiscountConfig).all()
    for config in discount_configs:
        if config.min_amount <= amount <= config.max_amount:
            return amount * config.discount_rate
    return amount
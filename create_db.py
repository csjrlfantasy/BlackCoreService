from app import app, db

# 创建数据库表
with app.app_context():
    db.create_all()
    print("Database tables created successfully.")
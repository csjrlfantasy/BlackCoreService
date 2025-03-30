# 添加必要的导入
from flask import Blueprint, jsonify, request
from flasgger import swag_from  # 必须添加这个导入
import hashlib

# 共享同一个蓝图对象（需从主路由文件导入）
from routes.productServices.get_products import get_products_bp

# 确保装饰器在导入之后
@get_products_bp.route('/product_services/generate_sign', methods=['POST'])
@swag_from({  # 现在swag_from已正确定义
    'summary': '生成签名验证',
    'tags': ['商品管理服务'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'nickname': {'type': 'string'},
                    'md5_value': {'type': 'string'}
                },
                'required': ['username', 'nickname', 'md5_value']
            }
        }
    ],
    'responses': {
        200: {'description': '签名验证成功'},
        400: {'description': '参数不完整或验证失败'}
    }
})
def generate_sign():
    # 获取POST请求数据
    data = request.get_json()
    required_fields = ['username', 'nickname', 'md5_value']  # 移除了phone字段
    if not data or any(field not in data for field in required_fields):
        return jsonify({"message": "参数不完整"}), 400
    
    # 提取参数
    username = data['username']
    nickname = data['nickname']
    client_md5 = data['md5_value']  # 移除了phone参数
    
    try:
        # 生成服务端MD5（移除了phone拼接）
        expected_str = f"{username}{nickname}".encode('utf-8')
        print(f"调试信息 - 原始字符串: {username}{nickname}")
        calculated_md5 = hashlib.md5(expected_str).hexdigest()
        
        # 比对MD5值
        if calculated_md5 == client_md5:
            return jsonify({
                "message": "验证成功",
                "data": {
                    "username": username,
                    "nickname": nickname
                }
            }), 200
        else:
            return jsonify({"message": "MD5校验失败"}), 400
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": "服务器处理错误"}), 500
from flasgger import swag_from
from flask import Blueprint, request, jsonify
from models import db
from datetime import datetime
from plugin.encryption import encrypt_aes, decrypt_aes
import uuid
from sqlalchemy import text


agreement_sign_bp = Blueprint('agreement_sign', __name__)


@agreement_sign_bp.route('/agreementSign', methods=['POST'])
@swag_from({
    'summary': 'Agreement Pre-Sign',
    'description': 'Initiates an agreement pre-sign process.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'serviceCode': {'type': 'string', 'example': 'C0001'},
                    'merchantNo': {'type': 'string', 'example': '893002075272'},
                    'requestNo': {'type': 'string', 'example': 'HEI1615882557427'},
                    'requestTime': {'type': 'integer', 'example': 1615884035855},
                    'charset': {'type': 'string', 'example': 'UTF-8'},
                    'bizContent': {'type': 'string', 'example': 'VqyzjmegowA96A5d2lKTPa2530mXaNucHrXE38xAVyvJo5pwyBa0XR7gTde/4MuzGFdI/W5CkEofWcUj/MGUyykT8Jc+dm3Dfg/DKvGVpyhM2Cscs292HBTeVEEU5UJsPib1hRKYpru6YbOIcP3ly5A17RsRcRV7+4ZBcMCbnCS8beXOaXfYYBIXm72FUtg6vqshnrdQ/BZ6n9a43yIyC6NyN70yuxk3GGaOk4g+tBM='}
                },
                'required': ['serviceCode', 'merchantNo', 'requestNo', 'requestTime', 'bizContent']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Agreement Pre-Sign Successful',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'code': {'type': 'string', 'example': '0000'},
                            'msg': {'type': 'string', 'example': 'Success'},
                            'resultContent': {'type': 'string', 'example': 'EncryptedResponseData'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad Request',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'code': {'type': 'string', 'example': '1001'},
                            'msg': {'type': 'string', 'example': 'Invalid Parameters'}
                        }
                    }
                }
            }
        },
        500: {
            'description': 'Internal Server Error',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'code': {'type': 'string', 'example': '5000'},
                            'msg': {'type': 'string', 'example': 'Server Error'}
                        }
                    }
                }
            }
        }
    }
})
def agreement_sign():
    data = request.json
    service_code = data.get('serviceCode')
    merchant_no = data.get('merchantNo')
    request_no = data.get('requestNo')
    request_time = data.get('requestTime')
    charset = data.get('charset', 'UTF-8')
    biz_content_encrypted = data.get('bizContent')

    # 解析和验证请求参数
    if not all([service_code, merchant_no, request_no, request_time, biz_content_encrypted]):
        return jsonify({"code": "4001", "msg": "Missing required parameters"}), 400

    # 解密业务内容（bizContent）
    try:
        biz_content = decrypt_aes(biz_content_encrypted)
    except Exception as e:
        print("Decryption error:", str(e))
        return jsonify({"code": "4002", "msg": "Failed to decrypt bizContent"}), 400

    # 模拟业务逻辑处理（如验证用户信息）
    # 在实际应用中，这里会调用其他服务来验证 bizContent 中的业务参数

    # 构建响应内容并加密
    response_data = {
        "respCode": "0000",
        "respMsg": "操作成功",
        "traceNo": str(uuid.uuid4())  # 生成唯一的 traceNo
    }
    result_content_encrypted = encrypt_aes(str(response_data))

    # 将请求数据存入数据库
    db.session.execute(text("""
        INSERT INTO agreement_requests (service_code, merchant_no, request_no, request_time, charset, biz_content, created_at)
        VALUES (:service_code, :merchant_no, :request_no, :request_time, :charset, :biz_content, :created_at)
    """), {
        "service_code": service_code,
        "merchant_no": merchant_no,
        "request_no": request_no,
        "request_time": request_time,
        "charset": charset,
        "biz_content": biz_content_encrypted,
        "created_at": datetime.utcnow()
    })

    # 将响应数据存入数据库
    db.session.execute(text("""
        INSERT INTO agreement_responses (request_no, code, msg, result_content, created_at)
        VALUES (:request_no, :code, :msg, :result_content, :created_at)
    """), {
        "request_no": request_no,
        "code": "0000",
        "msg": "签约成功",
        "result_content": result_content_encrypted,
        "created_at": datetime.utcnow()
    })

    db.session.commit()

    # 返回响应
    return jsonify({
        "code": "0000",
        "msg": "签约成功",
        "resultContent": result_content_encrypted
    }), 200

from flask import jsonify

def success(data=None, msg="成功", code=200):
    """
    成功响应
    :param data: 响应数据
    :param msg: 响应消息
    :param code: 响应状态码
    """
    response = {
        "code": code,
        "msg": msg,
        "data": data
    }
    return jsonify(response)

def error(msg="失败", code=400, data=None):
    """
    错误响应
    :param msg: 错误消息
    :param code: 错误状态码
    :param data: 额外的错误数据
    """
    response = {
        "code": code,
        "msg": msg,
        "data": data
    }
    return jsonify(response)
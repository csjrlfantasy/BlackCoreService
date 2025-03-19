from flask import Blueprint, send_from_directory, request, jsonify
from flasgger import swag_from
from werkzeug.utils import secure_filename
import os

# 创建独立的蓝图对象
file_bp = Blueprint('file_services', __name__)

# 配置文件上传参数
UPLOAD_FOLDER = 'e:/Program Files/pythonProject/BlackCoreService1.0/uploads'
ALLOWED_EXTENSIONS = {
    'txt': 'text/plain',
    'pdf': 'application/pdf',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'jar': 'application/java-archive'  # 新增JAR类型
}

@file_bp.route('/file_services/upload', methods=['POST'])
@swag_from({
    'summary': '文件上传接口',
    'tags': ['文件管理'],
    'consumes': ['multipart/form-data'],
    'parameters': [{
        'name': 'file',
        'in': 'formData',
        'type': 'file',
        'required': True,
        'description': '选择要上传的文件'
    }],
    'responses': {
        201: {'description': '文件上传成功'},
        400: {'description': '未选择文件或文件类型不合法'}
    }
})
def handle_upload():
    if 'file' not in request.files:
        return jsonify({"message": "未选择文件"}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"message": "无效文件"}), 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({
        "message": "文件上传成功",
        "filename": filename,
        "url": f"/file_services/download/{filename}"
    }), 201

@file_bp.route('/file_services/download/<filename>', methods=['GET'])
@swag_from({
    'summary': '文件下载接口',
    'tags': ['文件管理'],
    'parameters': [{
        'name': 'filename',
        'in': 'path',
        'type': 'string',
        'required': True
    }],
    'responses': {
        200: {'description': '文件下载成功'},
        404: {'description': '文件不存在'}
    }
})
def handle_download(filename):
    if not os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
        return jsonify({"message": "文件不存在"}), 404
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
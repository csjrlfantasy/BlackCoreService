from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flasgger import swag_from
import jwt
import datetime

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
@swag_from({
    'summary': 'User Registration',
    'description': 'Register a new user with username and password.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'user1'},
                    'password': {'type': 'string', 'example': 'password123'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        201: {'description': 'User registered successfully'},
        400: {'description': 'Error during registration'}
    }
})
def register():
    data = request.json
    existing_user = User.query.filter_by(username=data['username']).first()

    if existing_user:
        return jsonify({"message": "Username already exists!"}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password_hash=hashed_password, token="")
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

@bp.route('/login', methods=['POST'])
@swag_from({
    'summary': 'User Login',
    'description': 'Login and obtain JWT token.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'user1'},
                    'password': {'type': 'string', 'example': 'password123'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        200: {'description': 'JWT token generated'},
        401: {'description': 'Invalid credentials'}
    }
})
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"message": "Invalid credentials!"}), 401

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, config['SECRET_KEY'], algorithm="HS256")

    user.token = token
    db.session.commit()

    return jsonify({"token": token}), 200

from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.auth_utils import encode_auth_token
import base64

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.objects(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    if User.objects(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    user = User(
        username=data['username'],
        email=data['email'],
        is_dm=data['is_dm']
    )
    user.set_password(data['password'])
    user.save()
    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    auth_header = request.headers.get('Authorization')

    # if not auth_header or not auth_header.startswith('Basic '):
    #     return jsonify({'message': 'Authorization header is missing or invalid'}), 401

    # Decode the Basic Auth header
    try:
        auth_decoded = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
        username, password = auth_decoded.split(':')
    except (TypeError, ValueError, IndexError):
        return jsonify({'message': 'Invalid Authorization header format'}), 401

    # Authenticate the user
    user = User.objects(username=username).first()
    if user and user.check_password(password):
        auth_token = encode_auth_token(user.id, user.is_dm)
        if auth_token:
            return jsonify({'token': auth_token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.auth_utils import encode_auth_token
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from flask import current_app

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
    data = request.get_json()
    user = User.objects(username=data['username']).first()
    if user and user.check_password(data['password']):
        auth_token = encode_auth_token(user.id, user.is_dm)
        if auth_token:
            return jsonify({'token': auth_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

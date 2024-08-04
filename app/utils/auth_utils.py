from functools import wraps
from flask import request, jsonify, current_app
from app.models.user import User
import jwt
from datetime import datetime, timedelta

def encode_auth_token(user_id, **roles):
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': str(user_id)A
            'roles': roles
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

def token_required(required_roles=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization', None)
            if auth_header:
                try:
                    auth_type, token = auth_header.split()
                except ValueError:
                    return jsonify({'message': 'Invalid Authorization header format'}), 403

                if auth_type.lower() != 'bearer':
                    return jsonify({'message': 'Invalid token type. Expected Bearer token'}), 403
            else:
                return jsonify({'message': 'Authorization header is missing!'}), 403
            
            if not token:
                return jsonify({'message': 'Token is missing!'}), 403

            try:
                payload = decode_auth_token(token)
                user_id = payload['sub']
                current_user = User.objects(id=ObjectId(user_id)).first()

                if not current_user:
                    return jsonify({'message': 'User not found!'}), 403

                # Check for required roles in the token claims under 'roles'
                if required_roles:
                    roles = payload.get('roles', {})
                    for role in required_roles:
                        if not roles.get(role, False):
                            return jsonify({'message': f'Role {role} required!'}), 403

            except Exception as e:
                return jsonify({'message': str(e)}), 403

            return f(current_user, *args, **kwargs)
        
        return decorated_function
    return decorator

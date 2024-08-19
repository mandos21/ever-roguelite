import logging
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from bson import ObjectId
from flask import current_app, request, abort

from app.models.user import User

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)


def encode_auth_token(user_id, is_dm):
    try:
        payload = {
            'exp': datetime.now(timezone.utc) + timedelta(days=1),
            'iat': datetime.now(timezone.utc),
            'sub': str(user_id),
            'is_dm': is_dm
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception:
        logger.exception("Failed to encode auth token")
        return None


def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        abort(403, description='Signature expired. Please log in again.')
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        abort(403, description='Invalid token. Please log in again.')


def token_required(dm_required=False):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization', None)
            if auth_header is None:
                logger.warning("Authorization header is missing")
                abort(403, description='Authorization header is missing!')

            try:
                auth_type, token = auth_header.split()
                if auth_type.lower() != 'bearer':
                    logger.warning("Invalid token type: %s", auth_type)
                    abort(403, description='Invalid token type. Expected Bearer token')
            except ValueError:
                logger.warning("Invalid Authorization header format")
                abort(403, description='Invalid Authorization header format')

            if not token:
                logger.warning("Token is missing")
                abort(403, description='Token is missing!')

            try:
                payload = decode_auth_token(token)
                user_id = payload['sub']
                current_user = User.objects(id=ObjectId(user_id)).first()
                kwargs['current_user'] = current_user

                if current_user is None:
                    logger.warning("User not found")
                    abort(403, description='User not found!')

                if dm_required and not payload.get('is_dm', False):
                    logger.warning("DM required but not provided in token")
                    abort(403, description='DM required!')

            except Exception as e:
                logger.exception("Token validation error")
                abort(403, description=str(e))

            return f(*args, **kwargs)

        return decorated_function

    return decorator

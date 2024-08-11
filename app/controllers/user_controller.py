from bson import ObjectId
from flask import Blueprint, jsonify, request

from app.models.user import User
from app.utils.auth_utils import token_required

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/', methods=['GET'])
@token_required(dm_required=True)
def get_users(**kwargs):
    users = User.objects().all()
    users_list = []
    for user in users:
        users_list.append({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'is_dm': user.is_dm
        })

    return jsonify(users_list), 200


@user_bp.route('/items', methods=['GET'])
@token_required()
def get_items(*args, **kwargs):
    """
    Get items based on the provided parameters:
    - If `user_id` is provided, return that user's items.
    - If `all` is provided, return items for all users, optionally excluding `user_id`.
    - If neither is provided, return the current user's items.
    """
    try:
        user_id = request.args.get('user_id')
        all_users = request.args.get('all', '').lower() == 'true'

        def format_item(item):
            return {
                'id': str(item.id),
                'name': item.name,
                'description': item.description,
                'image': item.image_file_location,
                'unique': item.unique
            }

        def format_user(user):
            return {
                'user_id': str(user.id),
                'username': user.username,
                'email': user.email,
                'items': [format_item(item) for item in user.items]
            }

        if all_users:
            exclude_user_id = ObjectId(user_id) if user_id else None
            users = User.objects()
            users_data = [
                format_user(user) for user in users
                if not exclude_user_id or user.id != exclude_user_id
            ]
            return jsonify({'users': users_data}), 200

        else:
            target_user_id = ObjectId(user_id) if user_id else kwargs['current_user'].id
            user = User.objects(id=target_user_id).first()

            if not user:
                return jsonify({'message': 'User not found!'}), 404

            return jsonify(format_user(user)), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

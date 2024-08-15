from flask import Blueprint, request
from mongoengine import DoesNotExist

import json

from app.models.item import Item
from app.models.user import User
from app.utils.auth_utils import token_required

session_bp = Blueprint('session_bp', __name__)

@session_bp.route('/export', methods=['GET'])
@token_required(dm_required=True)
def export_session(**kwargs):
    session = {
        "user": [user.to_mongo().to_dict() for user in User.objects()],
        "item": [item.to_mongo().to_dict() for item in Item.objects()]
    }
    return json.dumps(session), 200


@session_bp.route('/import', methods=['POST'])
@token_required(dm_required=True)
def import_session(**kwargs):
    responses = {}
    data = request.get_json()

    for user_data in data['item']:
        try:
            item = Item.objects.get(unique=user_data['unique'])
            item.available = user_data['available']
            item.claimed = user_data['claimed']
            item.save()
            responses.add('200')
        except DoesNotExist:
            responses.add('400')

    for user_data in data['user']:
        try:
            user = User.objects.get(username=user_data['username'])
            user.items = user_data['items']
            user.save()
            responses.add('200')
        except DoesNotExist:
            responses.add('400')

    if '400' in responses:
        return 'one or more invalid values', 400
    elif '200' in responses:
        return 'import successful', 200


@session_bp.route('/clear', methods=['POST'])
@token_required(dm_required=True)
def clear_session(**kwargs):
    for user in User.objects().all():
        user.items = []
        user.save()
    for item in Item.objects().all():
        item.available = True
        item.claimed = False
        item.save()
    return '', 204

from flask import Blueprint, request, jsonify

from app.models.room import Room
from app.utils.auth_utils import token_required
from app.utils.crud_helpers import get_document, create_document, update_document, delete_document, get_all_documents

room_bp = Blueprint('room_bp', __name__)


@room_bp.route('/', defaults={'room_id': None})
@room_bp.route('/<room_id>', methods=['GET'])
@token_required(dm_required=True)
def get_rooms(room_id, **kwargs):
    if room_id:
        return get_document(Room, room_id)
    return get_all_documents(Room)


@room_bp.route('/', methods=['POST'])
@token_required(dm_required=True)
def create_room(**kwargs):
    data = request.get_json()
    return create_document(Room, data)


@room_bp.route('/<room_id>', methods=['PATCH'])
@token_required(dm_required=True)
def update_room(room_id, **kwargs):
    data = request.get_json()
    room = Room.objects(id=room_id).first()
    if not room:
        return jsonify({'message': 'Room not found!'}), 404
    return update_document(room, data)


@room_bp.route('/<room_id>', methods=['DELETE'])
@token_required(dm_required=True)
def delete_room(room_id, **kwargs):
    room = Room.objects(id=room_id).first()
    if not room:
        return jsonify({'message': 'Room not found!'}), 404
    return delete_document(room)

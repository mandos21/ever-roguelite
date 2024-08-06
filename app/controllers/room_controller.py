from flask import Blueprint, request
from app.utils.auth_utils import token_required
from app.utils.crud_helpers import get_document, create_document, update_document, delete_document, get_all_documents
from app.models.room import Room


room_bp = Blueprint('room_bp', __name__)

@room_bp.route('/rooms', methods=['GET'])
@token_required(required_roles=['is_dm'])
def get_rooms(current_user):
    room_id = request.args.get('id')
    if room_id:
        return get_document_or_404(Room, room_id)
    return get_all_documents(Room)

@room_bp.route('/rooms', methods=['POST'])
@token_required(required_roles=['is_dm'])
def create_room(current_user):
    data = request.get_json()
    return create_document(Room, data)

@room_bp.route('/rooms/<room_id>', methods=['PATCH'])
@token_required(required_roles=['is_dm'])
def update_room(current_user, room_id):
    data = request.get_json()
    room = Room.objects(id=room_id).first()
    if not room:
        return jsonify({'message': 'Room not found!'}), 404
    return update_document(room, data)

@room_bp.route('/rooms/<room_id>', methods=['DELETE'])
@token_required(required_roles=['is_dm'])
def delete_room(current_user, room_id):
    room = Room.objects(id=room_id).first()
    if not room:
        return jsonify({'message': 'Room not found!'}), 404
    return delete_document(room)

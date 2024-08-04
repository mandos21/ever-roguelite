from flask import Blueprint, request
from app.utils.auth_utils import token_required
from app.utils.crud_helpers import get_document, create_document, update_document, delete_document, get_all_documents
from app.models.item import Item

item_bp = Blueprint('item_bp', __name__)

@item_bp.route('/items', methods=['GET'])
@token_required(required_roles=['is_dm'])
def get_items(current_user):
    item_id = request.args.get('id')
    if item_id:
        return get_document_or_404(Item, item_id)
    return get_all_documents(Item)

@item_bp.route('/items', methods=['POST'])
@token_required(required_roles=['is_dm'])
def create_item(current_user):
    data = request.get_json()
    return create_document(Item, data)

@item_bp.route('/items/<item_id>', methods=['PATCH'])
@token_required(required_roles=['is_dm'])
def update_item(current_user, item_id):
    data = request.get_json()
    item = Item.objects(id=item_id).first()
    if not item:
        return jsonify({'message': 'Item not found!'}), 404
    return update_document(item, data)

@item_bp.route('/items/<item_id>', methods=['DELETE'])
@token_required(required_roles=['is_dm'])
def delete_item(current_user, item_id):
    item = Item.objects(id=item_id).first()
    if not item:
        return jsonify({'message': 'Item not found!'}), 404
    return delete_document(item)

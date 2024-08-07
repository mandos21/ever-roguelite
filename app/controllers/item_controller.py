from flask import Blueprint, request
from app.utils.auth_utils import token_required
from app.utils.crud_helpers import get_document, create_document, update_document, delete_document, get_all_documents
from app.models.item import Item

item_bp = Blueprint('item_bp', __name__)

@item_bp.route('/', methods=['GET'])
@token_required(dm_required=True)
def get_items(current_user):
    item_id = request.args.get('id')
    if item_id:
        return get_document_or_404(Item, item_id)
    return get_all_documents(Item)

@item_bp.route('/', methods=['POST'])
@token_required(dm_required=True)
def create_item(current_user):
    data = request.get_json()
    return create_document(Item, data)

@item_bp.route('/<item_id>', methods=['PATCH'])
@token_required(dm_required=True)
def update_item(current_user, item_id):
    data = request.get_json()
    item = Item.objects(id=item_id).first()
    if not item:
        return jsonify({'message': 'Item not found!'}), 404
    return update_document(item, data)

@item_bp.route('/<item_id>', methods=['DELETE'])
@token_required(dm_required=True)
def delete_item(current_user, item_id):
    item = Item.objects(id=item_id).first()
    if not item:
        return jsonify({'message': 'Item not found!'}), 404
    return delete_document(item)

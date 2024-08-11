from flask import Blueprint, request, jsonify

from app.models.item import Item
from app.utils.auth_utils import token_required
from app.utils.crud_helpers import get_document, create_document, update_document, delete_document, get_all_documents

item_bp = Blueprint('item_bp', __name__)


@item_bp.route('/', defaults={'item_id': None})
@item_bp.route('/<item_id>', methods=['GET'])
@token_required(dm_required=True)
def get_items(**kwargs):
    item_id = request.args.get('item_id')
    if item_id:
        return get_document(Item, item_id)
    return get_all_documents(Item)


@item_bp.route('/', methods=['POST'])
@token_required(dm_required=True)
def create_item(**kwargs):
    data = request.get_json()
    return create_document(Item, data)


@item_bp.route('/<item_id>', methods=['PATCH'])
@token_required(dm_required=True)
def update_item(item_id, **kwargs):
    data = request.get_json()
    item = Item.objects(id=item_id).first()
    if not item:
        return jsonify({'message': 'Item not found!'}), 404
    return update_document(item, data)


@item_bp.route('/<item_id>', methods=['DELETE'])
@token_required(dm_required=True)
def delete_item(item_id, **kwargs):
    item = Item.objects(id=item_id).first()
    if not item:
        return jsonify({'message': 'Item not found!'}), 404
    return delete_document(item)

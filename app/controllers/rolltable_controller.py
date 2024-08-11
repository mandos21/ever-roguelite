from flask import Blueprint, request, jsonify

from app.models.rolltable import RollTable
from app.utils.auth_utils import token_required
from app.utils.crud_helpers import get_document, create_document, update_document, delete_document, get_all_documents

rolltable_bp = Blueprint('rolltable_bp', __name__)


@rolltable_bp.route('/', defaults={'rolltable_id': None})
@rolltable_bp.route('/<rolltable_id>', methods=['GET'])
@token_required(dm_required=True)
def get_rolltables(**kwargs):
    rolltable_id = request.args.get('rolltable_id')
    if rolltable_id:
        return get_document(RollTable, rolltable_id)
    return get_all_documents(RollTable)


@rolltable_bp.route('/', methods=['POST'])
@token_required(dm_required=True)
def create_rolltable(**kwargs):
    data = request.get_json()
    return create_document(RollTable, data)


@rolltable_bp.route('/<rolltable_id>', methods=['PATCH'])
@token_required(dm_required=True)
def update_rolltable(rolltable_id, **kwargs):
    data = request.get_json()
    rolltable = RollTable.objects(id=rolltable_id).first()
    if not rolltable:
        return jsonify({'message': 'RollTable not found!'}), 404
    return update_document(rolltable, data)


@rolltable_bp.route('/<rolltable_id>', methods=['DELETE'])
@token_required(dm_required=True)
def delete_rolltable(rolltable_id, **kwargs):
    rolltable = RollTable.objects(id=rolltable_id).first()
    if not rolltable:
        return jsonify({'message': 'RollTable not found!'}), 404
    return delete_document(rolltable)

from flask import Blueprint, request
from app.utils.auth_utils import dm_required
from app.utils.crud_helpers import get_document, create_document, update_document, delete_document, get_all_documents
from app.models.rolltable import RollTable

@rolltable_bp.route('/rolltables', methods=['GET'])
@token_required(required_roles=['is_dm'])
def get_rolltables(current_user):
    rolltable_id = request.args.get('id')
    if rolltable_id:
        return get_document_or_404(RollTable, rolltable_id)
    return get_all_documents(RollTable)

@rolltable_bp.route('/rolltables', methods=['POST'])
@token_required(required_roles=['is_dm'])
def create_rolltable(current_user):
    data = request.get_json()
    return create_document(RollTable, data)

@rolltable_bp.route('/rolltables/<rolltable_id>', methods=['PATCH'])
@token_required(required_roles=['is_dm'])
def update_rolltable(current_user, rolltable_id):
    data = request.get_json()
    rolltable = RollTable.objects(id=rolltable_id).first()
    if not rolltable:
        return jsonify({'message': 'RollTable not found!'}), 404
    return update_document(rolltable, data)

@rolltable_bp.route('/rolltables/<rolltable_id>', methods=['DELETE'])
@token_required(required_roles=['is_dm'])
def delete_rolltable(current_user, rolltable_id):
    rolltable = RollTable.objects(id=rolltable_id).first()
    if not rolltable:
        return jsonify({'message': 'RollTable not found!'}), 404
    return delete_document(rolltable)

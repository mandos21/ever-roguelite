from flask import Blueprint, request
from app.utils.auth_utils import token_required
from app.utils.crud_helpers import get_document, create_document, update_document, delete_document, get_all_documents
from app.models.encounter import Encounter

encounter_bp = Blueprint('encounter_bp', __name__)

@encounter_bp.route('/encounters', methods=['GET'])
@token_required(required_roles=['is_dm'])
def get_encounters(current_user):
    encounter_id = request.args.get('id')
    if encounter_id:
        return get_document_or_404(Encounter, encounter_id)
    return get_all_documents(Encounter)

@encounter_bp.route('/encounters', methods=['POST'])
@token_required(required_roles=['is_dm'])
def create_encounter(current_user):
    data = request.get_json()
    return create_document(Encounter, data)

@encounter_bp.route('/encounters/<encounter_id>', methods=['PATCH'])
@token_required(required_roles=['is_dm'])
def update_encounter(current_user, encounter_id):
    data = request.get_json()
    encounter = Encounter.objects(id=encounter_id).first()
    if not encounter:
        return jsonify({'message': 'Encounter not found!'}), 404
    return update_document(encounter, data)

@encounter_bp.route('/encounters/<encounter_id>', methods=['DELETE'])
@token_required(required_roles=['is_dm'])
def delete_encounter(current_user, encounter_id):
    encounter = Encounter.objects(id=encounter_id).first()
    if not encounter:
        return jsonify({'message': 'Encounter not found!'}), 404
    return delete_document(encounter)

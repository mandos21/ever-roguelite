from flask import Blueprint, request, jsonify

from app.models.encounter import Encounter
from app.utils.auth_utils import token_required
from app.utils.crud_helpers import get_document, create_document, update_document, delete_document, get_all_documents

encounter_bp = Blueprint('encounter_bp', __name__)


@encounter_bp.route('/', defaults={'encounter_id': None})
@encounter_bp.route('/<encounter_id>', methods=['GET'])
@token_required(dm_required=True)
def get_encounters(encounter_id, **kwargs):
    if encounter_id:
        return get_document(Encounter, encounter_id)
    return get_all_documents(Encounter)


@encounter_bp.route('/', methods=['POST'])
@token_required(dm_required=True)
def create_encounter(**kwargs):
    data = request.get_json()
    return create_document(Encounter, data)


@encounter_bp.route('/<encounter_id>', methods=['PATCH'])
@token_required(dm_required=True)
def update_encounter(encounter_id, **kwargs):
    data = request.get_json()
    encounter = Encounter.objects(id=encounter_id).first()
    if not encounter:
        return jsonify({'message': 'Encounter not found!'}), 404
    return update_document(encounter, data)


@encounter_bp.route('/<encounter_id>', methods=['DELETE'])
@token_required(dm_required=True)
def delete_encounter(encounter_id, **kwargs):
    encounter = Encounter.objects(id=encounter_id).first()
    if not encounter:
        return jsonify({'message': 'Encounter not found!'}), 404
    return delete_document(encounter)

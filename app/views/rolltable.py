from bson import ObjectId
from flask import Blueprint, jsonify, request

from app.models.rolltable import RollTable
from app.utils.auth_utils import token_required
from app.utils.crud_helpers import (
    create_document,
    delete_document,
    get_all_documents,
    get_document,
    modify_document,
    update_document,
)

rolltable_bp = Blueprint("rolltable_bp", __name__)


@rolltable_bp.route("/", defaults={"rolltable_id": None})
@rolltable_bp.route("/<rolltable_id>", methods=["GET"])
@token_required(dm_required=True)
def get_rolltables(rolltable_id, **kwargs):
    if rolltable_id:
        return get_document(RollTable, rolltable_id)
    return get_all_documents(RollTable)


@rolltable_bp.route("/", methods=["POST"])
@token_required(dm_required=True)
def create_rolltable(**kwargs):
    data = request.get_json()
    return create_document(RollTable, data)


@rolltable_bp.route("/<rolltable_id>", methods=["PATCH"])
@token_required(dm_required=True)
def update_rolltable(rolltable_id, **kwargs):
    data = request.get_json()
    rolltable = RollTable.objects(id=rolltable_id).first()
    if not rolltable:
        return jsonify({"message": "RollTable not found!"}), 404
    return update_document(rolltable, data)


@rolltable_bp.route("/<rolltable_id>/add", methods=["POST"])
@token_required(dm_required=True)
def add_to_rolltable(rolltable_id, **kwargs):
    data = request.get_json()
    rolltable = RollTable.objects(id=ObjectId(rolltable_id)).first()
    if not rolltable:
        return jsonify({"message": "RollTable not found!"}), 404
    update_data = {}

    if "items" in data.keys():
        update_data["add_to_set__items"] = data["items"]
    elif "encounters" in data.keys():
        update_data["add_to_set__encounters"] = data["encounters"]
    elif "rooms" in data.keys():
        update_data["add_to_set__rooms"] = data["rooms"]
    else:
        return jsonify({"message": "No valid fields to update!"}), 400

    return modify_document(rolltable, update_data)


@rolltable_bp.route("/<rolltable_id>", methods=["DELETE"])
@token_required(dm_required=True)
def delete_rolltable(rolltable_id, **kwargs):
    rolltable = RollTable.objects(id=rolltable_id).first()
    if not rolltable:
        return jsonify({"message": "RollTable not found!"}), 404
    return delete_document(rolltable)

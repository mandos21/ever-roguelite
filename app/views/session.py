from bson import ObjectId
from flask import Blueprint, jsonify, request
from mongoengine import DoesNotExist

from app.models.item import Item
from app.models.user import User
from app.utils.auth_utils import token_required

session_bp = Blueprint("session_bp", __name__)


def clear_session_data():
    for user in User.objects().all():
        user.items = []
        user.save()
    for item in Item.objects().all():
        item.available = True
        item.claimed = False
        item.save()


@session_bp.route("/clear", methods=["POST"])
@token_required(dm_required=True)
def clear_session(**kwargs):
    clear_session_data()
    return "", 204


@session_bp.route("/export", methods=["GET"])
@token_required(dm_required=True)
def export_session(**kwargs):
    session = {
        "user": [user.to_mongo().to_dict() for user in User.objects()],
        "item": [item.to_mongo().to_dict() for item in Item.objects()],
    }
    return jsonify(session), 200


@session_bp.route("/import", methods=["POST"])
@token_required(dm_required=True)
def import_session(**kwargs):
    data = request.get_json()
    clear_session_data()
    user_count = 0
    item_count = 0

    for user_data in data["user"]:
        try:
            user = User.objects.get(username=user_data["username"])
            user.items = [ObjectId(item_id) for item_id in user_data["items"]]
            user.save()
            user_count += 1
        except DoesNotExist:
            clear_session_data()
            return jsonify({"message": "One or more invalid fields"}), 400

    for item_data in data["item"]:
        try:
            item = Item.objects.get(id=ObjectId(item_data["_id"]))
            item.available = item_data["available"]
            item.claimed = item_data["claimed"]
            item.save()
            item_count += 1
        except DoesNotExist:
            clear_session_data()
            return jsonify({"message": "One or more invalid fields"}), 400

    return (
        jsonify(
            {"message": f"{user_count} users and {item_count} items imported"}
        ),
        200,
    )

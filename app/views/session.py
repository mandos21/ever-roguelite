from flask import Blueprint

from app.models.item import Item
from app.models.user import User
from app.utils.auth_utils import token_required

session_bp = Blueprint("session_bp", __name__)


@session_bp.route("/clear", methods=["POST"])
@token_required(dm_required=True)
def clear_session(**kwargs):
    for user in User.objects().all():
        user.items = []
        user.save()
    for item in Item.objects().all():
        item.available = True
        item.claimed = False
        item.save()
    return "", 204

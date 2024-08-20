from mongoengine import BooleanField, StringField

from app.models.rollable import Rollable


class Item(Rollable):
    type = StringField(default="Item")
    unique = BooleanField(default=True, required=True)
    claimed = BooleanField(default=False, required=True)  # for playthrough
    has_been_rolled = BooleanField(default=False, required=True)
    available = BooleanField(default=True)  # for current round of rolling
    image_file_location = StringField()
    meta = {"collection": "rollable_items"}

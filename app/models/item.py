from mongoengine import EmbeddedDocument, StringField
from app.models.base import Rollable

class Item(Rollable):
    type = StringField(default="Item")
    currency = BooleanField(default=False)
    meta = {
        'collection': 'rollable_items'
    }

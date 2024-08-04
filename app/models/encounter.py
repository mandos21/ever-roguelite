from mongoengine import StringField, ListField
from app.models.rollable import Rollable

class Encounter(Rollable):
    type = StringField(default="Encounter")
    min_players = IntField(required=True)
    max_players = IntField(required=True)

    meta = {
        'collection': 'rollable_encounters'
    }

from mongoengine import Document, ListField, ReferenceField, StringField
from app.models.item import Item
from app.models.boss import Boss
from app.models.room import Room
from app.models.encounter import Encounter

class RollTable(Rollable):
    tier = StringField(required=True, choices=["Platinum", "Gold", "Silver", "Bronze"])
    table_type = StringField(required=True, choices=["Items", "Encounters"])
    items = ListField(ReferenceField(Item))
    encounters = ListField(ReferenceField(Encounter))

    meta = {
        'collection': 'rolltables'
    }

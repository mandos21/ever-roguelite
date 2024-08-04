from mongoengine import Document, ListField, ReferenceField, StringField
from app.models.item import Item
from app.models.room import Room
from app.models.rollable import Rollable
from app.models.encounter import Encounter

class RollTable(Rollable):
    tier = StringField(required=True, choices=["Platinum", "Gold", "Silver", "Bronze"])
    table_type = StringField(required=True, choices=["Magic Items","Weapons", "Encounters", "Rooms"])
    
    items = ListField(ReferenceField(Item))
    encounters = ListField(ReferenceField(Encounter))
    rooms = ListField(ReferenceField(Room))
    meta = {
        'collection': 'rolltables'
    }

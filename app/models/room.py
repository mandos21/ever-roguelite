from mongoengine import StringField
from app.models.rollable import Rollable

class Room(Rollable):
    type = StringField(default="Room")
    reward_tier = String(choices=["Bronze", "Silver", "Gold", "Platinum"])
    meta = {
        'collection': 'rollable_rooms'
    }

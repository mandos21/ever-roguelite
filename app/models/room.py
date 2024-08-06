from mongoengine import StringField
from app.models.rollable import Rollable

class Room(Rollable):
    type = StringField(default="Room")
    reward_tier = StringField(choices=["Bronze", "Silver", "Gold", "Platinum"])
    meta = {
        'collection': 'rollable_rooms'
    }

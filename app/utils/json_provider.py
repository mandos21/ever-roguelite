from bson import ObjectId
from flask.json.provider import DefaultJSONProvider


class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

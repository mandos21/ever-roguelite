from mongoengine import Document, IntField, StringField


class Rollable(Document):
    meta = {"abstract": True}

    name = StringField(required=True)
    description = StringField(require=True)
    weight = IntField(required=True, min_value=1, default=1)

    def __str__(self):
        return self.name

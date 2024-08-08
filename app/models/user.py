from mongoengine import EmbeddedDocument, StringField, BooleanField, ListField, EmailField, Document, ReferenceField
from app.models.rolltable import Rollable
from app.models.item import Item
from werkzeug.security import generate_password_hash, check_password_hash

class User(Document):
    type = StringField(default="User")
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    is_active = BooleanField(default=False)
    is_dm = BooleanField(default=False, required=True)
    items = ListField(ReferenceField(Item))
    meta = {
        'collection': 'users'
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
import unittest
from mongoengine import connect, disconnect
from app.models.encounter import Encounter
from app.models.item import Item
from app.models.rolltable import RollTable
from app.models.room import Room
from app.models.user import User


class MongoEngineTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
        # Connect to a test database
        connect('mongoenginetest', alias='default', uuidRepresentation='standard')

    @classmethod
    def tearDownClass(cls):
        # Disconnect from the test database
        disconnect(alias='default')

    def setUp(self):
        # Clear the database before each test
        Encounter.drop_collection()
        Item.drop_collection()
        RollTable.drop_collection()
        Room.drop_collection()
        User.drop_collection()

    def test_encounter_creation(self):
        encounter = Encounter(name="Test Encounter", description="An encounter", min_players=1, max_players=4)
        encounter.save()
        self.assertEqual(encounter.type, "Encounter")
        self.assertEqual(encounter.min_players, 1)
        self.assertEqual(encounter.max_players, 4)

    def test_item_creation(self):
        item = Item(name="Test Item", description="An item", unique=True, claimed=False, has_been_rolled=False,
                    available=True)
        item.save()
        self.assertEqual(item.type, "Item")
        self.assertTrue(item.unique)
        self.assertFalse(item.claimed)
        self.assertFalse(item.has_been_rolled)
        self.assertTrue(item.available)

    def test_rolltable_creation(self):
        rolltable = RollTable(name="Test RollTable", description="A rolltable", weight=5, tier="Gold",
                              table_type="Magic Items")
        rolltable.save()
        self.assertEqual(rolltable.tier, "Gold")
        self.assertEqual(rolltable.table_type, "Magic Items")

    def test_room_creation(self):
        room = Room(name="Test Room", description="A room", reward_tier="Silver")
        room.save()
        self.assertEqual(room.type, "Room")
        self.assertEqual(room.reward_tier, "Silver")

    def test_user_creation(self):
        user = User(username="testuser", email="testuser@example.com", password_hash="password_hash", is_active=True,
                    is_dm=True)
        user.set_password("password")
        user.save()
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_dm)
        self.assertTrue(user.check_password("password"))

    def test_rolltable_with_items(self):
        item1 = Item(name="Item1", description="First item", unique=True, claimed=False, has_been_rolled=False,
                     available=True).save()
        item2 = Item(name="Item2", description="Second item", unique=True, claimed=False, has_been_rolled=False,
                     available=True).save()
        rolltable = RollTable(name="Item RollTable", description="Table of items", weight=1, tier="Bronze",
                              table_type="Magic Items", items=[item1, item2])
        rolltable.save()
        retrieved_rolltable = RollTable.objects(id=rolltable.id).first()
        self.assertEqual(len(retrieved_rolltable.items), 2)
        self.assertIn(item1, retrieved_rolltable.items)
        self.assertIn(item2, retrieved_rolltable.items)


if __name__ == '__main__':
    unittest.main()

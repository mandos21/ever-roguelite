import base64
import unittest

from mongoengine import disconnect

from app import create_app
from app.models.item import Item
from app.models.user import User


class SessionViewTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        disconnect(alias="default")
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        disconnect(alias="default")

    def setUp(self):
        # Clean up the database before each test
        User.drop_collection()
        Item.drop_collection()

        # Create a DM user and log in
        self.dm_user = User(
            username="dmuser", email="dmuser@example.com", is_dm=True
        )
        self.dm_user.set_password("password")
        self.dm_user.save()

        # Log in as DM to get a token
        credentials = base64.b64encode(b"dmuser:password").decode("utf-8")
        response = self.client.post(
            "/auth/login", headers={"Authorization": f"Basic {credentials}"}
        )
        self.token = response.json["token"]

        # Create a regular user
        self.regular_user = User(
            username="regularuser",
            email="regularuser@example.com",
            is_dm=False,
        )
        self.regular_user.set_password("password")
        self.regular_user.items = []
        self.regular_user.save()

        # Create items and assign some to the regular user
        self.item1 = Item(
            name="Sword of Testing",
            description="A powerful sword",
            weight=10,
            available=False,
            claimed=True,
        ).save()
        self.item2 = Item(
            name="Shield of Testing",
            description="A sturdy shield",
            weight=15,
            available=False,
            claimed=True,
        ).save()
        self.regular_user.items.extend([self.item1, self.item2])
        self.regular_user.save()

    def test_clear_session(self):
        # Test clearing session as DM
        response = self.client.post(
            "/session/clear", headers={"Authorization": f"Bearer {self.token}"}
        )

        self.assertEqual(response.status_code, 204)

        # Ensure that the user's items were cleared
        user = User.objects(id=self.regular_user.id).first()
        self.assertEqual(len(user.items), 0)

        # Ensure that the items were reset
        item1 = Item.objects(id=self.item1.id).first()
        item2 = Item.objects(id=self.item2.id).first()
        self.assertTrue(item1.available)
        self.assertFalse(item1.claimed)
        self.assertTrue(item2.available)
        self.assertFalse(item2.claimed)

    def test_clear_session_as_non_dm(self):
        # Log in as a regular user to get a token
        credentials = base64.b64encode(b"regularuser:password").decode("utf-8")
        response = self.client.post(
            "/auth/login", headers={"Authorization": f"Basic {credentials}"}
        )
        non_dm_token = response.json["token"]

        # Attempt to clear session as a non-DM user
        response = self.client.post(
            "/session/clear",
            headers={"Authorization": f"Bearer {non_dm_token}"},
        )

        self.assertEqual(response.status_code, 403)  # Expecting Forbidden

    def test_clear_session_without_token(self):
        # Attempt to clear session without providing a token
        response = self.client.post("/session/clear")

        self.assertEqual(response.status_code, 403)  # Expecting Forbidden


if __name__ == "__main__":
    unittest.main()

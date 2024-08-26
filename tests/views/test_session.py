import base64
import json
import unittest

from app.models.item import Item
from app.models.user import User
from tests.views.test_view_base import ViewTestBase, drop_all_collections


class SessionViewTestCase(ViewTestBase):

    def setUp(self):
        super().setUp()


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

    def test_export_session(self):
        # Call the export_session route
        response = self.client.get(
            "/session/export",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200

        session_data = json.loads(response.data)

        assert len(session_data["user"]) == 2
        assert len(session_data["item"]) == 2
        assert session_data["user"][0]["username"] == "dmuser"
        assert session_data["item"][0]["name"] == "Sword of Testing"
        assert session_data["user"][1]["username"] == "regularuser"
        assert session_data["item"][1]["name"] == "Shield of Testing"

    def test_import_session(self):
        # Add initial mock data to be imported
        import_data = {
            "item": [
                {
                    "_id": str(Item.objects.get(name="Sword of Testing").id),
                    "available": False,
                    "claimed": True,
                },
                {
                    "_id": str(Item.objects.get(name="Shield of Testing").id),
                    "available": False,
                    "claimed": True,
                },
            ],
            "user": [
                {"username": "dmuser", "items": []},
                {
                    "username": "regularuser",
                    "items": [
                        str(Item.objects.get(name="Sword of Testing").id),
                        str(Item.objects.get(name="Shield of Testing").id),
                    ],
                },
            ],
        }

        # Call the import_session route

        response = self.client.post(
            "/session/import",
            data=json.dumps(import_data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200

        # Check the response message
        response_data = json.loads(response.data)
        assert response_data["message"] == "2 users and 2 items imported"

        # Verify the imported data
        dmuser = User.objects.get(username="dmuser")
        assert dmuser.get_item_names() == []

        regularuser = User.objects.get(username="regularuser")
        assert regularuser.get_item_names() == [
            "Sword of Testing",
            "Shield of Testing",
        ]

        item = Item.objects.get(name="Sword of Testing")
        assert item.available is False
        assert item.claimed is True

    def test_import_session_invalid_user(self):
        # Mock invalid data with a non-existent user
        import_data = {
            "user": [{"username": "non_existent_user", "items": ["item1"]}],
            "item": [
                {
                    "_id": "1",
                    "name": "Laptop",
                    "available": False,
                    "claimed": True,
                }
            ],
        }

        # Call the import_session route with invalid data
        response = self.client.post(
            "/session/import",
            data=json.dumps(import_data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.token}"},
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["message"] == "One or more invalid fields"

        # Verify that no data was imported
        for user in User.objects.all():
            assert user.items == []
        for item in Item.objects.all():
            assert item.available == True
            assert item.claimed == False

    def test_import_session_invalid_item(self):
        # Mock invalid data with a non-existent item
        import_data = {
            "user": [{"username": "john_doe", "items": ["item1", "item2"]}],
            "item": [
                {
                    "_id": "999",  # Non-existent item ID
                    "name": "NonExistentItem",
                    "available": False,
                    "claimed": True,
                }
            ],
        }

        # Call the import_session route with invalid data
        response = self.client.post(
            "/session/import",
            data=json.dumps(import_data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["message"] == "One or more invalid fields"

        # Verify that no data was imported
        for user in User.objects.all():
            assert user.items == []
        for item in Item.objects.all():
            assert item.available == True
            assert item.claimed == False


if __name__ == "__main__":
    unittest.main()

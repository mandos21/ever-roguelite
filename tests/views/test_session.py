import base64
import unittest
import json

from mongoengine import disconnect

from app import create_app
from app.models.item import Item
from app.models.user import User


class SessionControllerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        disconnect(alias='default')
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        disconnect(alias='default')

    def setUp(self):
        # Clean up the database before each test
        User.drop_collection()
        Item.drop_collection()

        # Create a DM user and log in
        self.dm_user = User(username='dmuser', email='dmuser@example.com', is_dm=True)
        self.dm_user.set_password('password')
        self.dm_user.save()

        # Log in as DM to get a token
        credentials = base64.b64encode(b'dmuser:password').decode('utf-8')
        response = self.client.post('/auth/login', headers={
            'Authorization': f'Basic {credentials}'
        })
        self.token = response.json['token']

        # Create a regular user
        self.regular_user = User(username='regularuser', email='regularuser@example.com', is_dm=False)
        self.regular_user.set_password('password')
        self.regular_user.items = []
        self.regular_user.save()

        # Create items and assign some to the regular user
        self.item1 = Item(name="Sword of Testing", description="A powerful sword", weight=10, available=False,
                          claimed=True).save()
        self.item2 = Item(name="Shield of Testing", description="A sturdy shield", weight=15, available=False,
                          claimed=True).save()
        self.regular_user.items.extend([self.item1, self.item2])
        self.regular_user.save()

    def test_clear_session(self):
        # Test clearing session as DM
        response = self.client.post('/session/clear', headers={
            'Authorization': f'Bearer {self.token}'
        })

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
        credentials = base64.b64encode(b'regularuser:password').decode('utf-8')
        response = self.client.post('/auth/login', headers={
            'Authorization': f'Basic {credentials}'
        })
        non_dm_token = response.json['token']

        # Attempt to clear session as a non-DM user
        response = self.client.post('/session/clear', headers={
            'Authorization': f'Bearer {non_dm_token}'
        })

        self.assertEqual(response.status_code, 403)  # Expecting Forbidden

    def test_clear_session_without_token(self):
        # Attempt to clear session without providing a token
        response = self.client.post('/session/clear')

        self.assertEqual(response.status_code, 403)  # Expecting Forbidden
    
    def test_export_session(self):
        # Add mock data
        user = User(username="john_doe", items=["item1", "item2"]).save()
        item = Item(name="Laptop", available=False, claimed=True).save()

        # Call the export_session route
        response = self.client.get('/export')

        assert response.status_code == 200

        session_data = json.loads(response.data)

        assert len(session_data['user']) == 1
        assert len(session_data['item']) == 1
        assert session_data['user'][0]['username'] == "john_doe"
        assert session_data['item'][0]['name'] == "Laptop"

    def test_import_session(self):
        # Add initial mock data to be imported
        import_data = {
            "user": [
                {
                    "username": "john_doe",
                    "items": ["item1", "item2"]
                }
            ],
            "item": [
                {
                    "_id": "1",
                    "name": "Laptop",
                    "available": False,
                    "claimed": True
                }
            ]
        }

        # Call the import_session route
        response = self.client.post('/import', data=json.dumps(import_data), content_type='application/json')

        assert response.status_code == 200

        # Check the response message
        response_data = json.loads(response.data)
        assert response_data['message'] == "1 users and 1 items imported"

        # Verify the imported data
        user = User.objects.get(username="john_doe")
        assert user.items == ["item1", "item2"]

        item = Item.objects.get(name="Laptop")
        assert item.available is False
        assert item.claimed is True

    def test_import_session_invalid_user(self):
        # Mock invalid data with a non-existent user
        import_data = {
            "user": [
                {
                    "username": "non_existent_user",
                    "items": ["item1"]
                }
            ],
            "item": [
                {
                    "_id": "1",
                    "name": "Laptop",
                    "available": False,
                    "claimed": True
                }
            ]
        }

        # Call the import_session route with invalid data
        response = self.client.post('/import', data=json.dumps(import_data), content_type='application/json')

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['message'] == "One or more invalid fields"

        # Verify that no data was imported
        assert User.objects.count() == 0
        assert Item.objects.count() == 0

    def test_import_session_invalid_item(self):
        # Mock invalid data with a non-existent item
        import_data = {
            "user": [
                {
                    "username": "john_doe",
                    "items": ["item1", "item2"]
                }
            ],
            "item": [
                {
                    "_id": "999",  # Non-existent item ID
                    "name": "NonExistentItem",
                    "available": False,
                    "claimed": True
                }
            ]
        }

        # Call the import_session route with invalid data
        response = self.client.post('/import', data=json.dumps(import_data), content_type='application/json')

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['message'] == "One or more invalid fields"

        # Verify that no data was imported
        assert User.objects.count() == 0
        assert Item.objects.count() == 0


if __name__ == '__main__':
    unittest.main()

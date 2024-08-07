import unittest
from app import create_app
from app.models.item import Item
from app.models.user import User
from mongoengine import connect, disconnect

class ItemControllerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        disconnect(alias='default')

    def setUp(self):
        Item.drop_collection()
        User.drop_collection()
        # Create a DM user and log in for authenticated routes
        self.dm_user = User(username='dmuser', email='dmuser@example.com', is_dm=True)
        self.dm_user.set_password('password')
        self.dm_user.save()
        response = self.client.post('/auth/login', json={
            'username': 'dmuser',
            'password': 'password'
        })
        self.token = response.json['token']

    def tearDown(self):
        Item.drop_collection()
        User.drop_collection()

    def test_create_item(self):
        content = {
            'name': 'Test Item',
            'description': 'An item',
            'unique': True,
            'claimed': False,
            'has_been_rolled': False,
            'available': True                                                                                                                     }
        response = self.client.post('/items/', json=content, headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()
        self.assertIsNotNone(response_data.pop("_id", None))

        for k,v in content.items():
            self.assertEqual(response_data[k], v)


    def test_get_items(self):
        item = Item(name='Test Item', description='An item', unique=True)
        item.save()
        response = self.client.get('/items/', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIsInstance(response_data, list)
        self.assertGreaterEqual(len(response_data), 1)
        self.assertIn('name', response_data[0])
        self.assertEqual(response_data[0]['name'], 'Test Item')

    def test_update_item(self):
        item = Item(name='Test Item', description='An item', unique=True)
        item.save()
        response = self.client.patch(f'/items/{item.id}', json={
            'description': 'Updated description'
        }, headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data['description'], 'Updated description')

    def test_delete_item(self):
        item = Item(name='Test Item', description='An item', unique=True)
        item.save()
        response = self.client.delete(f'/items/{item.id}', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Item deleted successfully!')

if __name__ == '__main__':
    unittest.main()

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
        disconnect()

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
        response = self.client.post('/items', json={
            'name': 'Test Item',
            'description': 'An item',
            'unique': True,
            'claimed': False,
            'has_been_rolled': False,
            'available': True
        }, headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 201)

    def test_get_items(self):
        Item(name='Test Item', description='An item', unique=True).save()
        response = self.client.get('/items', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json), 1)

    def test_update_item(self):
        item = Item(name='Test Item', description='An item', unique=True).save()
        response = self.client.patch(f'/items/{item.id}', json={
            'description': 'Updated description'
        }, headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['description'], 'Updated description')

    def test_delete_item(self):
        item = Item(name='Test Item', description='An item', unique=True).save()
        response = self.client.delete(f'/items/{item.id}', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

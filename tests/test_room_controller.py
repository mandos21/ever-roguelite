import unittest
from app import create_app
from app.models.room import Room
from app.models.user import User
from mongoengine import connect, disconnect
from flask import json

class RoomControllerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        disconnect(alias='default')

    def setUp(self):
        Room.drop_collection()
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
        Room.drop_collection()
        User.drop_collection()

    def test_create_room(self):
        content = {
            'name': 'Test Room',
            'description': 'A room',
            'reward_tier': 'Gold'
        }
        response = self.client.post('/rooms/', json=content, headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()
        
        # Assert that the _id field is present and then remove it from the response data
        self.assertIsNotNone(response_data.pop("_id", None))

        # Check if all the fields in content match the response_data
        for key, value in content.items():
            self.assertEqual(response_data[key], value)

    def test_get_rooms(self):
        room = Room(name='Test Room', description='A room', reward_tier='Gold')
        room.save()
        response = self.client.get('/rooms/', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIsInstance(response_data, list)
        self.assertGreaterEqual(len(response_data), 1)
        self.assertIn('name', response_data[0])
        self.assertEqual(response_data[0]['name'], 'Test Room')

    def test_update_room(self):
        room = Room(name='Test Room', description='A room', reward_tier='Gold')
        room.save()
        response = self.client.patch(f'/rooms/{room.id}', json={
            'description': 'Updated description'
        }, headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data['description'], 'Updated description')

    def test_delete_room(self):
        room = Room(name='Test Room', description='A room', reward_tier='Gold')
        room.save()
        response = self.client.delete(f'/rooms/{room.id}', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Room deleted successfully!')

if __name__ == '__main__':
    unittest.main()

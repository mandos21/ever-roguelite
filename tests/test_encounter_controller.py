import unittest
from app import create_app
from app.models.encounter import Encounter
from app.models.user import User
from mongoengine import connect, disconnect
from flask import json

class EncounterControllerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        disconnect(alias='default')

    def setUp(self):
        Encounter.drop_collection()
        User.drop_collection()
        self.dm_user = User(username='dmuser', email='dmuser@example.com', is_dm=True)
        self.dm_user.set_password('password')
        self.dm_user.save()
        response = self.client.post('/auth/login', json={
            'username': 'dmuser',
            'password': 'password'
        })
        self.token = response.json['token']

    def tearDown(self):
        Encounter.drop_collection()
        User.drop_collection()

    def test_create_encounter(self):
        content = {
            'name': 'Test Encounter',
            'description': 'An encounter',
            'min_players': 1,
            'max_players': 4
        }
        response = self.client.post('/encounters/', json=content, headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()
        
        self.assertIsNotNone(response_data.pop("_id", None))

        for key, value in content.items():
            self.assertEqual(response_data[key], value)

    def test_get_encounters(self):
        encounter = Encounter(name='Test Encounter', description='An encounter', min_players=1, max_players=4)
        encounter.save()
        response = self.client.get('/encounters/', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIsInstance(response_data, list)
        self.assertGreaterEqual(len(response_data), 1)
        self.assertIn('name', response_data[0])
        self.assertEqual(response_data[0]['name'], 'Test Encounter')

    def test_update_encounter(self):
        encounter = Encounter(name='Test Encounter', description='An encounter', min_players=1, max_players=4)
        encounter.save()
        response = self.client.patch(f'/encounters/{encounter.id}', json={
            'description': 'Updated description'
        }, headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data['description'], 'Updated description')

    def test_delete_encounter(self):
        encounter = Encounter(name='Test Encounter', description='An encounter', min_players=1, max_players=4)
        encounter.save()
        response = self.client.delete(f'/encounters/{encounter.id}', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Encounter deleted successfully!')

if __name__ == '__main__':
    unittest.main()
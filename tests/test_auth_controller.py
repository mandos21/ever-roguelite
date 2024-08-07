import unittest
from app import create_app
from app.models.user import User
from mongoengine import connect, disconnect

class AuthControllerTestCase(unittest.TestCase):

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
        #connect('mongoenginetest', alias='default')
        User.drop_collection()

    def test_register_user(self):
        response = self.client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password',
            'is_dm': True
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'User registered successfully')

    def test_register_user_existing_username(self):
        User(username='testuser', email='test1@example.com', password_hash='hash').save()
        response = self.client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Username already exists')

    def test_login_user(self):
        user = User(username='testuser', email='testuser@example.com')
        user.set_password('password')
        user.save()
        response = self.client.post('/auth/login', json={
            'username': 'testuser',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)

    def test_login_user_invalid_credentials(self):
        response = self.client.post('/auth/login', json={
            'username': 'wronguser',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid credentials')

if __name__ == '__main__':
    unittest.main()

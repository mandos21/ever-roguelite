import unittest
import base64
from app import create_app
from app.models.user import User
from mongoengine import disconnect, get_db


def drop_all_collections():
    db = get_db()
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)


class ControllerTestBase(unittest.TestCase):

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
        drop_all_collections()
        self.dm_user = User(username='dmuser', email='dmuser@example.com', is_dm=True)
        self.dm_user.set_password('password')
        self.dm_user.save()

        credentials = base64.b64encode(b'dmuser:password').decode('utf-8')
        response = self.client.post('/auth/login', headers={
            'Authorization': f'Basic {credentials}'
        })
        self.token = response.json['token']


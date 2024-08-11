import base64
import unittest

from app.models.item import Item
from app.models.user import User
from tests.controllers.controller_test_base import ControllerTestBase


class UserControllerTestCase(ControllerTestBase):

    def test_get_current_user_items(self):
        item = Item(name='Test Item',
                    description='A test item',
                    unique=True, claimed=False,
                    has_been_rolled=False,
                    available=True)
        item.save()
        self.dm_user.items.append(item)
        self.dm_user.save()
        response = self.client.get('/users/items', headers={'Authorization': f'Bearer {self.token}'})

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data['username'], 'dmuser')
        self.assertEqual(len(response_data['items']), 1)
        self.assertEqual(response_data['items'][0]['name'], 'Test Item')

    def test_get_specific_user_items(self):
        other_user = User(username='otheruser', email='otheruser@example.com', is_dm=False)
        other_user.set_password('password')
        item = Item(name='Other Test Item',
                    description='Another test item',
                    unique=True,
                    claimed=False,
                    has_been_rolled=False,
                    available=True)
        item.save()
        other_user.items.append(item)
        other_user.save()
        response = self.client.get(f'/users/items?user_id={other_user.id}',
                                   headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data['username'], 'otheruser')
        self.assertEqual(len(response_data['items']), 1)
        self.assertEqual(response_data['items'][0]['name'], 'Other Test Item')

    def test_get_all_users_items(self):
        other_user = User(username='otheruser', email='otheruser@example.com', is_dm=False)
        other_user.set_password('password')
        item1 = Item(name='Test Item 1',
                     description='First test item',
                     unique=True,
                     claimed=False,
                     has_been_rolled=False,
                     available=True)
        item2 = Item(name='Test Item 2',
                     description='Second test item',
                     unique=True,
                     claimed=False,
                     has_been_rolled=False,
                     available=True)
        item1.save()
        item2.save()
        self.dm_user.items.append(item1)
        other_user.items.append(item2)
        self.dm_user.save()
        other_user.save()
        response = self.client.get('/users/items?all=true', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(len(response_data['users']), 2)
        user_data = {user['username']: user for user in response_data['users']}
        self.assertEqual(len(user_data['dmuser']['items']), 1)
        self.assertEqual(user_data['dmuser']['items'][0]['name'], 'Test Item 1')
        self.assertEqual(len(user_data['otheruser']['items']), 1)
        self.assertEqual(user_data['otheruser']['items'][0]['name'], 'Test Item 2')

    def test_get_all_users_items_exclude_user(self):
        other_user = User(username='otheruser', email='otheruser@example.com', is_dm=False)
        other_user.set_password('password')
        item1 = Item(name='Test Item 1',
                     description='First test item',
                     unique=True,
                     claimed=False,
                     has_been_rolled=False,
                     available=True)
        item2 = Item(name='Test Item 2',
                     description='Second test item',
                     unique=True,
                     claimed=False,
                     has_been_rolled=False,
                     available=True)
        item1.save()
        item2.save()
        self.dm_user.items.append(item1)
        other_user.items.append(item2)
        self.dm_user.save()
        other_user.save()
        response = self.client.get(f'/users/items?all=true&user_id={self.dm_user.id}',
                                   headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(len(response_data['users']), 1)
        self.assertEqual(response_data['users'][0]['username'], 'otheruser')
        self.assertEqual(len(response_data['users'][0]['items']), 1)
        self.assertEqual(response_data['users'][0]['items'][0]['name'], 'Test Item 2')

    def test_get_user_items_user_not_found(self):
        response = self.client.get('/users/items?user_id=604c6e206c8e4a7f94b2b2a3',
                                   headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 404)
        response_data = response.get_json()
        self.assertEqual(response_data['message'], 'User not found!')

    def test_get_users_as_dm(self):
        self.regular_user = User(username='regular_user', email='regular@example.com', is_dm=False)
        self.regular_user.set_password('password')
        self.regular_user.save()

        credentials = base64.b64encode(b'regular_user:password').decode('utf-8')
        response = self.client.post('/auth/login', headers={
            'Authorization': f'Basic {credentials}'
        })
        self.non_admin_token = response.json['token']

        # Test that DM can access the user list
        response = self.client.get('/users/', headers={
            'Authorization': f'Bearer {self.token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        usernames = [user['username'] for user in response.json]
        self.assertIn('dmuser', usernames)
        self.assertIn('regular_user', usernames)

    def test_get_users_as_non_dm(self):
        self.regular_user = User(username='regular_user', email='regular@example.com', is_dm=False)
        self.regular_user.set_password('password')
        self.regular_user.save()

        credentials = base64.b64encode(b'regular_user:password').decode('utf-8')
        response = self.client.post('/auth/login', headers={
            'Authorization': f'Basic {credentials}'
        })
        self.non_admin_token = response.json['token']

        # Test that a non-DM cannot access the user list
        response = self.client.get('/users/', headers={
            'Authorization': f'Bearer {self.non_admin_token}'
        })
        print(response.json)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_get_users_no_token(self):
        # Test that no token results in unauthorized access
        response = self.client.get('/users/')
        print(response.json)
        self.assertEqual(response.status_code, 403)  # Forbidden


if __name__ == '__main__':
    unittest.main()

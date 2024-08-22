import unittest

from app import socketio
from app.models.user import User
from tests.views.test_view_base import ViewTestBase


class SocketNamespaceTestCase(ViewTestBase):

    def setUp(self):
        super().setUp()
        self.socket_client = socketio.test_client(
            self.app,
            namespace='/socket',
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def test_connect_disconnect(self):
        # Test connection (client connects automatically upon instantiation)
        received = self.socket_client.get_received('/socket')
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'system_message')
        self.assertIn('dmuser has connected.', received[0]['args'][0]['msg'])

        # Test disconnection
        self.socket_client.disconnect(namespace='/socket')
        self.assertFalse(self.socket_client.is_connected(namespace='/socket'))

    def test_system_message(self):
        self.socket_client.get_received('/socket')  # get the connect message out of the received
        # Test sending a system message
        self.socket_client.emit('system_message', {'message': 'Brandon has chosen the steel longsword'},
                                namespace='/socket')
        received = self.socket_client.get_received('/socket')
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'system_message')
        self.assertIn('Brandon has chosen the steel longsword', received[0]['args'][0]['msg'])

    def test_dm_message_to_all(self):
        self.socket_client.get_received('/socket')  # get the connect message out of the received
        # Test DM message to all users
        self.socket_client.emit('dm_message', {'message': 'You may now roll for an item!'}, namespace='/socket')
        received = self.socket_client.get_received('/socket')
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'dm_message')
        self.assertIn('You may now roll for an item!', received[0]['args'][0]['msg'])

    def test_dm_message_to_specific_users(self):
        self.socket_client.get_received('/socket')  # get the connect message out of the received
        # Create additional users
        players = []
        for i in range(0, 2):
            players.append(User(username=f'player{i}', email=f'player{i}@example.com'))
            players[i].set_password('password')
            players[i].save()

        # Join players to their rooms based on their IDs
        self.socket_client.emit('join_room', {'username': 'player1', 'room': str(players[0].id)}, namespace='/socket')
        self.socket_client.emit('join_room', {'username': 'player2', 'room': str(players[1].id)}, namespace='/socket')

        # Test DM message to specific users
        self.socket_client.emit('dm_message', {
            'message': 'You have been granted permission to roll!',
            'usernames': ['player1', 'player2']
        }, namespace='/socket')

        received = self.socket_client.get_received('/socket')
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'dm_message')
        self.assertIn('You have been granted permission to roll!', received[0]['args'][0]['msg'])


if __name__ == '__main__':
    unittest.main()

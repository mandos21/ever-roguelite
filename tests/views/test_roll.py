import unittest

from mongoengine import disconnect

from app import create_app
from app.models.encounter import Encounter
from app.models.item import Item
from app.models.rolltable import RollTable
from app.models.room import Room


class RollViewTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        disconnect(alias='default')

    def setUp(self):
        RollTable.drop_collection()
        Item.drop_collection()
        Encounter.drop_collection()
        Room.drop_collection()
        self.rolltable = RollTable(
            name='Test RollTable',
            description='A test rolltable',
            weight=5,
            tier='Gold',
            table_type='Weapons'
        )
        self.rolltable.save()

    def tearDown(self):
        RollTable.drop_collection()
        Item.drop_collection()
        Encounter.drop_collection()
        Room.drop_collection()

    def test_perform_roll_with_items(self):
        item1 = Item(name='Item 1', description='First item', unique=True, claimed=False, has_been_rolled=False,
                     available=True)
        item2 = Item(name='Item 2', description='Second item', unique=True, claimed=False, has_been_rolled=False,
                     available=True)
        item1.save()
        item2.save()
        self.rolltable.items = [item1, item2]
        self.rolltable.save()

        response = self.client.post('/rolls/', json={
            'rolltable_id': str(self.rolltable.id),
            'num_results': 1,
            'constraints': {}
        })

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('results', response_data)
        self.assertEqual(len(response_data['results']), 1)

    def test_perform_roll_no_results(self):
        response = self.client.post('/rolls/', json={
            'rolltable_id': str(self.rolltable.id),
            'num_results': 1,
            'constraints': {}
        })

        self.assertEqual(response.status_code, 204)

    def test_perform_roll_with_constraints(self):
        item1 = Item(name='Item 1', description='First item', unique=True, claimed=False, has_been_rolled=False,
                     available=True)
        item2 = Item(name='Item 2', description='Second item', unique=True, claimed=True, has_been_rolled=False,
                     available=True)
        item1.save()
        item2.save()
        self.rolltable.items = [item1, item2]
        self.rolltable.save()

        response = self.client.post('/rolls/', json={
            'rolltable_id': str(self.rolltable.id),
            'num_results': 1,
            'constraints': {'claimed': False}
        })

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('results', response_data)
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response_data['results'][0]['name'], 'Item 1')

    def test_perform_roll_invalid_rolltable(self):
        response = self.client.post('/rolls/', json={
            'rolltable_id': 'aaaaaaaaaaaaaaaaaaaaaaaa',
            'num_results': 1,
            'constraints': {}
        })
        self.assertEqual(response.status_code, 404)
        response_data = response.get_json()
        self.assertEqual(response_data['message'], 'RollTable not found!')


if __name__ == '__main__':
    unittest.main()

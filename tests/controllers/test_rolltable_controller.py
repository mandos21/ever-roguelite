import unittest
from app.models.rolltable import RollTable
from tests.controllers.controller_test_base import ControllerTestBase


class RollTableControllerTestCase(ControllerTestBase):

    def test_create_rolltable(self):
        content = {
            'name': 'Test RollTable',
            'description': 'A rolltable',
            'weight': 5,
            'tier': 'Gold',
            'table_type': 'Magic Items'
        }
        response = self.client.post('/rolltables/', json=content, headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()

        # Assert that the _id field is present and then remove it from the response data
        self.assertIsNotNone(response_data.pop("_id", None))

        # Check if all the fields in content match the response_data
        for key, value in content.items():
            self.assertEqual(response_data[key], value)

    def test_get_rolltables(self):
        rolltable = RollTable(name='Test RollTable',
                              description='A rolltable',
                              weight=5, tier='Gold',
                              table_type='Magic Items')
        rolltable.save()
        response = self.client.get('/rolltables/', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIsInstance(response_data, list)
        self.assertGreaterEqual(len(response_data), 1)
        self.assertIn('name', response_data[0])
        self.assertEqual(response_data[0]['name'], 'Test RollTable')

    def test_update_rolltable(self):
        rolltable = RollTable(name='Test RollTable',
                              description='A rolltable',
                              weight=5, tier='Gold',
                              table_type='Magic Items')
        rolltable.save()
        response = self.client.patch(f'/rolltables/{rolltable.id}', json={
            'description': 'Updated description'
        }, headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data['description'], 'Updated description')

    def test_delete_rolltable(self):
        rolltable = RollTable(name='Test RollTable',
                              description='A rolltable',
                              weight=5, tier='Gold',
                              table_type='Magic Items')
        rolltable.save()
        response = self.client.delete(f'/rolltables/{rolltable.id}', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'RollTable deleted successfully!')


if __name__ == '__main__':
    unittest.main()

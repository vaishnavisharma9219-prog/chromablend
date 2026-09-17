from tests.test_base import BaseTestCase

class TestEmergency(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.register("SafetyUser", "safety@example.com", "pass123")
        self.unlock_private("1984")

    def test_contacts_crud(self):
        # Create contact
        c_res = self.client.post('/api/contacts', json={
            'name': 'Sarah Sister',
            'phone': '+1 (555) 234-5678',
            'relationship': 'Sister',
            'notes': 'Lives nearby, has spare keys',
            'is_primary': 1
        })
        self.assertEqual(c_res.status_code, 201)
        contact_id = c_res.get_json()['data']['id']

        # Read
        get_res = self.client.get(f'/api/contacts/{contact_id}')
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.get_json()['data']['name'], 'Sarah Sister')
        self.assertEqual(get_res.get_json()['data']['is_primary'], 1)

        # Add second contact set as primary, ensure only one is primary
        c2_res = self.client.post('/api/contacts', json={
            'name': 'Dr. Marcus',
            'phone': '+1 (555) 876-5432',
            'relationship': 'Physician',
            'is_primary': 1
        })
        self.assertEqual(c2_res.status_code, 201)

        # Check Sarah is no longer primary
        sarah = self.client.get(f'/api/contacts/{contact_id}').get_json()['data']
        self.assertEqual(sarah['is_primary'], 0)

        # Delete contact
        del_res = self.client.delete(f'/api/contacts/{contact_id}')
        self.assertEqual(del_res.status_code, 200)

    def test_sos_workflow_and_honest_reporting(self):
        # Add a primary contact first
        self.client.post('/api/contacts', json={
            'name': 'Emergency Buddy',
            'phone': '+15559998888',
            'relationship': 'Friend',
            'is_primary': 1
        })

        # Trigger SOS
        sos_res = self.client.post('/api/emergency/sos', json={
            'notes': 'Walking to parking garage at night'
        })
        self.assertEqual(sos_res.status_code, 201)
        data = sos_res.get_json()['data']

        # Verify honest status structure
        self.assertEqual(data['status'], 'RECORDED')
        self.assertIn("not connected to this prototype", data['message'])
        self.assertIsNotNone(data['primary_contact'])
        self.assertEqual(data['primary_contact']['name'], 'Emergency Buddy')
        self.assertEqual(data['primary_contact']['phone'], '+15559998888')

        # Check history
        h_res = self.client.get('/api/emergency/history')
        self.assertEqual(h_res.status_code, 200)
        history = h_res.get_json()['data']
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['notes'], 'Walking to parking garage at night')

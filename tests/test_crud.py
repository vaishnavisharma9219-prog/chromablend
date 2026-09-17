from tests.test_base import BaseTestCase

class TestCRUD(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.register("Tester", "tester@example.com", "pass123")

    def test_tasks_crud_cycle(self):
        # Create
        c_res = self.client.post('/api/tasks', json={
            'title': 'Buy groceries',
            'description': 'Milk, bread, eggs',
            'date': '2026-09-18',
            'time': '10:00',
            'priority': 'high'
        })
        self.assertEqual(c_res.status_code, 201)
        task_id = c_res.get_json()['data']['id']

        # Read
        r_res = self.client.get(f'/api/tasks/{task_id}')
        self.assertEqual(r_res.status_code, 200)
        self.assertEqual(r_res.get_json()['data']['title'], 'Buy groceries')
        self.assertEqual(r_res.get_json()['data']['completed'], 0)

        # Toggle complete
        t_res = self.client.patch(f'/api/tasks/{task_id}/toggle')
        self.assertEqual(t_res.status_code, 200)
        self.assertEqual(t_res.get_json()['data']['completed'], 1)

        # Update
        u_res = self.client.put(f'/api/tasks/{task_id}', json={
            'title': 'Buy organic groceries',
            'description': 'Almond milk, rye bread',
            'date': '2026-09-18',
            'time': '11:00',
            'completed': 1,
            'priority': 'normal'
        })
        self.assertEqual(u_res.status_code, 200)
        self.assertEqual(u_res.get_json()['data']['title'], 'Buy organic groceries')

        # Delete
        d_res = self.client.delete(f'/api/tasks/{task_id}')
        self.assertEqual(d_res.status_code, 200)

        # Verify deletion
        v_res = self.client.get(f'/api/tasks/{task_id}')
        self.assertEqual(v_res.status_code, 404)

    def test_notes_crud_cycle(self):
        # Create
        c_res = self.client.post('/api/notes', json={
            'title': 'Design inspiration',
            'content': 'Minimalist warm tones and clean serif typography',
            'color_tag': 'lavender'
        })
        self.assertEqual(c_res.status_code, 201)
        note_id = c_res.get_json()['data']['id']

        # Search notes
        s_res = self.client.get('/api/notes?search=Minimalist')
        self.assertEqual(s_res.status_code, 200)
        self.assertEqual(len(s_res.get_json()['data']), 1)

        # Update
        u_res = self.client.put(f'/api/notes/{note_id}', json={
            'title': 'Design notes updated',
            'content': 'Revised styling guidelines',
            'color_tag': 'sage'
        })
        self.assertEqual(u_res.status_code, 200)
        self.assertEqual(u_res.get_json()['data']['color_tag'], 'sage')

        # Delete
        d_res = self.client.delete(f'/api/notes/{note_id}')
        self.assertEqual(d_res.status_code, 200)

        self.assertEqual(self.client.get(f'/api/notes/{note_id}').status_code, 404)

    def test_planner_crud_cycle(self):
        # Create morning and afternoon entries
        p1 = self.client.post('/api/planner', json={
            'date': '2026-09-20',
            'section': 'morning',
            'content': 'Team standup'
        })
        self.assertEqual(p1.status_code, 201)
        p1_id = p1.get_json()['data']['id']

        p2 = self.client.post('/api/planner', json={
            'date': '2026-09-20',
            'section': 'afternoon',
            'content': 'Deep work session'
        })
        self.assertEqual(p2.status_code, 201)

        # Fetch planner for that date
        get_p = self.client.get('/api/planner?date=2026-09-20')
        self.assertEqual(get_p.status_code, 200)
        data = get_p.get_json()['data']
        self.assertEqual(len(data['morning']), 1)
        self.assertEqual(len(data['afternoon']), 1)
        self.assertEqual(len(data['evening']), 0)

        # Update entry
        u_p = self.client.put(f'/api/planner/{p1_id}', json={'content': 'Extended team standup'})
        self.assertEqual(u_p.status_code, 200)
        self.assertEqual(u_p.get_json()['data']['content'], 'Extended team standup')

        # Delete entry
        d_p = self.client.delete(f'/api/planner/{p1_id}')
        self.assertEqual(d_p.status_code, 200)

        get_p2 = self.client.get('/api/planner?date=2026-09-20')
        self.assertEqual(len(get_p2.get_json()['data']['morning']), 0)

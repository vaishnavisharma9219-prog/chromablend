import io
from tests.test_base import BaseTestCase

class TestDataIsolation(BaseTestCase):
    def test_complete_user_data_isolation(self):
        # 1. Register User A
        res_a = self.register("User A", "user_a@example.com", "passwordA", "1111")
        self.assertEqual(res_a.status_code, 201)
        self.unlock_private("1111")

        # Create Task for User A
        t_res = self.client.post('/api/tasks', json={'title': 'User A Secret Task', 'date': '2026-09-17'})
        self.assertEqual(t_res.status_code, 201)
        task_a_id = t_res.get_json()['data']['id']

        # Create Note for User A
        n_res = self.client.post('/api/notes', json={'title': 'User A Private Note', 'content': 'Confidential info'})
        self.assertEqual(n_res.status_code, 201)
        note_a_id = n_res.get_json()['data']['id']

        # Create Planner Entry for User A
        p_res = self.client.post('/api/planner', json={'date': '2026-09-17', 'section': 'morning', 'content': 'Morning coffee'})
        self.assertEqual(p_res.status_code, 201)
        planner_a_id = p_res.get_json()['data']['id']

        # Create Contact for User A
        c_res = self.client.post('/api/contacts', json={'name': 'User A Contact', 'phone': '+15551234', 'relationship': 'Family'})
        self.assertEqual(c_res.status_code, 201)
        contact_a_id = c_res.get_json()['data']['id']

        # Upload Document for User A
        test_file = (io.BytesIO(b"Confidential user A document content"), 'user_a_doc.txt')
        d_res = self.client.post(
            '/api/documents',
            data={'category': 'Identity', 'file': test_file},
            content_type='multipart/form-data'
        )
        self.assertEqual(d_res.status_code, 201)
        doc_a_id = d_res.get_json()['data']['id']

        # Trigger SOS for User A
        sos_res = self.client.post('/api/emergency/sos', json={'notes': 'User A test trigger'})
        self.assertEqual(sos_res.status_code, 201)

        # 2. Log out User A
        self.logout()

        # 3. Register and Log in as User B
        res_b = self.register("User B", "user_b@example.com", "passwordB", "2222")
        self.assertEqual(res_b.status_code, 201)
        self.unlock_private("2222")

        # 4. Verify User B sees NONE of User A's data in collection endpoints
        tasks_b = self.client.get('/api/tasks').get_json()['data']
        self.assertEqual(len(tasks_b), 0)

        notes_b = self.client.get('/api/notes').get_json()['data']
        self.assertEqual(len(notes_b), 0)

        planner_b = self.client.get('/api/planner?date=2026-09-17').get_json()['data']
        self.assertEqual(len(planner_b['morning']), 0)
        self.assertEqual(len(planner_b['all']), 0)

        contacts_b = self.client.get('/api/contacts').get_json()['data']
        self.assertEqual(len(contacts_b), 0)

        docs_b = self.client.get('/api/documents').get_json()['data']
        self.assertEqual(len(docs_b), 0)

        sos_history_b = self.client.get('/api/emergency/history').get_json()['data']
        self.assertEqual(len(sos_history_b), 0)

        # 5. Attempt direct ID tampering as User B targeting User A's resources
        # Read User A's task
        get_t = self.client.get(f'/api/tasks/{task_a_id}')
        self.assertEqual(get_t.status_code, 404)

        # Edit User A's task
        edit_t = self.client.put(f'/api/tasks/{task_a_id}', json={'title': 'Hacked title'})
        self.assertEqual(edit_t.status_code, 404)

        # Delete User A's task
        del_t = self.client.delete(f'/api/tasks/{task_a_id}')
        self.assertEqual(del_t.status_code, 404)

        # Read User A's note
        get_n = self.client.get(f'/api/notes/{note_a_id}')
        self.assertEqual(get_n.status_code, 404)

        # Edit User A's note
        edit_n = self.client.put(f'/api/notes/{note_a_id}', json={'title': 'Hacked note', 'content': 'Hijacked'})
        self.assertEqual(edit_n.status_code, 404)

        # Delete User A's note
        del_n = self.client.delete(f'/api/notes/{note_a_id}')
        self.assertEqual(del_n.status_code, 404)

        # Update User A's planner
        edit_p = self.client.put(f'/api/planner/{planner_a_id}', json={'content': 'Hijacked plan'})
        self.assertEqual(edit_p.status_code, 404)

        # Delete User A's planner
        del_p = self.client.delete(f'/api/planner/{planner_a_id}')
        self.assertEqual(del_p.status_code, 404)

        # Access User A's contact
        get_c = self.client.get(f'/api/contacts/{contact_a_id}')
        self.assertEqual(get_c.status_code, 404)

        # Delete User A's contact
        del_c = self.client.delete(f'/api/contacts/{contact_a_id}')
        self.assertEqual(del_c.status_code, 404)

        # Download User A's document
        dl_doc = self.client.get(f'/api/documents/{doc_a_id}/download')
        self.assertEqual(dl_doc.status_code, 404)

        # Delete User A's document
        del_doc = self.client.delete(f'/api/documents/{doc_a_id}')
        self.assertEqual(del_doc.status_code, 404)

        # 6. Log out User B and log back in as User A
        self.logout()
        login_a = self.login("user_a@example.com", "passwordA")
        self.assertEqual(login_a.status_code, 200)
        self.unlock_private("1111")

        # 7. Verify all User A's original data is completely intact
        tasks_a = self.client.get('/api/tasks').get_json()['data']
        self.assertEqual(len(tasks_a), 1)
        self.assertEqual(tasks_a[0]['title'], 'User A Secret Task')

        notes_a = self.client.get('/api/notes').get_json()['data']
        self.assertEqual(len(notes_a), 1)
        self.assertEqual(notes_a[0]['title'], 'User A Private Note')

        planner_a = self.client.get('/api/planner?date=2026-09-17').get_json()['data']
        self.assertEqual(len(planner_a['morning']), 1)
        self.assertEqual(planner_a['morning'][0]['content'], 'Morning coffee')

        contacts_a = self.client.get('/api/contacts').get_json()['data']
        self.assertEqual(len(contacts_a), 1)
        self.assertEqual(contacts_a[0]['name'], 'User A Contact')

        docs_a = self.client.get('/api/documents').get_json()['data']
        self.assertEqual(len(docs_a), 1)
        self.assertEqual(docs_a[0]['original_filename'], 'user_a_doc.txt')

        # Download file as User A -> succeeds!
        dl_ok = self.client.get(f'/api/documents/{doc_a_id}/download')
        self.assertEqual(dl_ok.status_code, 200)
        self.assertEqual(dl_ok.data, b"Confidential user A document content")
        dl_ok.close()

        sos_history_a = self.client.get('/api/emergency/history').get_json()['data']
        self.assertEqual(len(sos_history_a), 1)

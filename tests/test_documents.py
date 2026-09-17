import io
import os
from tests.test_base import BaseTestCase

class TestDocuments(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.register("DocUser", "doc@example.com", "pass123")
        self.unlock_private("1984")

    def test_document_upload_download_delete(self):
        # 1. Upload valid document
        file_content = b"Official identification scan data mock"
        upload_res = self.client.post(
            '/api/documents',
            data={
                'category': 'Identity',
                'file': (io.BytesIO(file_content), 'passport_scan.pdf')
            },
            content_type='multipart/form-data'
        )
        self.assertEqual(upload_res.status_code, 201)
        doc = upload_res.get_json()['data']
        doc_id = doc['id']
        self.assertEqual(doc['original_filename'], 'passport_scan.pdf')
        self.assertEqual(doc['category'], 'Identity')

        # 2. Verify file exists in uploads folder
        file_path = os.path.join(self.upload_path, doc['stored_filename'])
        self.assertTrue(os.path.exists(file_path))

        # 3. Download document
        dl_res = self.client.get(f'/api/documents/{doc_id}/download')
        self.assertEqual(dl_res.status_code, 200)
        self.assertEqual(dl_res.data, file_content)
        dl_res.close()

        # 4. List documents
        list_res = self.client.get('/api/documents')
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(len(list_res.get_json()['data']), 1)

        # 5. Delete document
        del_res = self.client.delete(f'/api/documents/{doc_id}')
        self.assertEqual(del_res.status_code, 200)

        # Verify disk removal
        self.assertFalse(os.path.exists(file_path))

        # Verify DB removal
        self.assertEqual(self.client.get(f'/api/documents/{doc_id}/download').status_code, 404)

    def test_unsupported_file_extension(self):
        upload_res = self.client.post(
            '/api/documents',
            data={
                'category': 'Other',
                'file': (io.BytesIO(b"malicious script"), 'hack.exe')
            },
            content_type='multipart/form-data'
        )
        self.assertEqual(upload_res.status_code, 400)

    def test_checklist_persists(self):
        # Get checklist
        res = self.client.get('/api/documents/checklist')
        self.assertEqual(res.status_code, 200)
        items = res.get_json()['data']
        self.assertTrue(len(items) > 0)

        # Toggle item
        t_res = self.client.post('/api/documents/checklist', json={
            'item_key': 'gov_id',
            'is_checked': True
        })
        self.assertEqual(t_res.status_code, 200)

        # Verify state
        res2 = self.client.get('/api/documents/checklist')
        gov_item = next(i for i in res2.get_json()['data'] if i['key'] == 'gov_id')
        self.assertTrue(gov_item['is_checked'])

import unittest
import os
import tempfile
import shutil
from backend.app import create_app
from backend.database.db import init_db

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_chroma.db')
        self.upload_path = os.path.join(self.temp_dir, 'uploads')
        os.makedirs(self.upload_path, exist_ok=True)

        self.app = create_app({
            'TESTING': True,
            'DATABASE_PATH': self.db_path,
            'UPLOAD_FOLDER': self.upload_path,
            'SECRET_KEY': 'test-secret-key-12345',
            'GEMINI_API_KEY': ''
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            init_db(self.app)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def register(self, name, email, password, passcode="1984"):
        return self.client.post('/api/auth/register', json={
            'name': name,
            'email': email,
            'password': password,
            'passcode': passcode
        })

    def login(self, email, password):
        return self.client.post('/api/auth/login', json={
            'email': email,
            'password': password
        })

    def logout(self):
        return self.client.post('/api/auth/logout')

    def unlock_private(self, passcode="1984"):
        return self.client.post('/api/private-access/verify', json={
            'passcode': passcode
        })

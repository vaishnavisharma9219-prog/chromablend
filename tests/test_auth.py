import json
from tests.test_base import BaseTestCase

class TestAuth(BaseTestCase):
    def test_register_success(self):
        res = self.register("Alice Morgan", "alice@example.com", "secret123", "4321")
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['email'], "alice@example.com")
        self.assertEqual(data['data']['name'], "Alice Morgan")
        # Ensure password hashes are never returned
        self.assertNotIn('password_hash', data['data'])
        self.assertNotIn('private_passcode_hash', data['data'])

    def test_register_duplicate_email_fails(self):
        self.register("Alice", "alice@example.com", "secret123")
        res2 = self.register("Alice 2", "alice@example.com", "anotherpwd")
        self.assertEqual(res2.status_code, 409)
        data = res2.get_json()
        self.assertFalse(data['success'])

    def test_register_validation_errors(self):
        res = self.register("", "invalid-email", "123", "abc")
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data['success'])

    def test_login_success_and_failure(self):
        self.register("Bob", "bob@example.com", "mypassword")
        self.logout()

        # Failed login
        fail_res = self.login("bob@example.com", "wrongpass")
        self.assertEqual(fail_res.status_code, 401)

        # Successful login
        ok_res = self.login("bob@example.com", "mypassword")
        self.assertEqual(ok_res.status_code, 200)
        data = ok_res.get_json()
        self.assertTrue(data['success'])

    def test_me_endpoint_requires_auth(self):
        res = self.client.get('/api/auth/me')
        self.assertEqual(res.status_code, 401)

        self.register("Charlie", "charlie@example.com", "password123")
        res2 = self.client.get('/api/auth/me')
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.get_json()['data']['email'], "charlie@example.com")

    def test_logout_clears_session(self):
        self.register("Dave", "dave@example.com", "password123")
        self.logout()
        res = self.client.get('/api/auth/me')
        self.assertEqual(res.status_code, 401)

    def test_private_passcode_verification(self):
        self.register("Eve", "eve@example.com", "password123", "9988")
        
        # Wrong passcode
        bad = self.unlock_private("0000")
        self.assertEqual(bad.status_code, 401)

        # Correct passcode
        good = self.unlock_private("9988")
        self.assertEqual(good.status_code, 200)
        self.assertTrue(good.get_json()['data']['unlocked'])

        # Check status
        status = self.client.get('/api/private-access/status')
        self.assertTrue(status.get_json()['data']['unlocked'])

        # Lock / Quick Exit
        lock = self.client.post('/api/private-access/lock')
        self.assertEqual(lock.status_code, 200)
        self.assertFalse(lock.get_json()['data']['unlocked'])

        status2 = self.client.get('/api/private-access/status')
        self.assertFalse(status2.get_json()['data']['unlocked'])

if __name__ == '__main__':
    unittest.main()

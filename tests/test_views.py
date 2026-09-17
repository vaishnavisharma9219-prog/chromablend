from tests.test_base import BaseTestCase

class TestViews(BaseTestCase):
    def test_html_pages_served(self):
        # Index
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Chroma Blend', res.data)
        res.close()

        # Login
        res_login = self.client.get('/login.html')
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Sign In', res_login.data)
        res_login.close()

        # Register
        res_reg = self.client.get('/register.html')
        self.assertEqual(res_reg.status_code, 200)
        self.assertIn(b'Create Account', res_reg.data)
        res_reg.close()

        # Planner
        res_plan = self.client.get('/planner.html')
        self.assertEqual(res_plan.status_code, 200)
        self.assertIn(b'Daily Agenda', res_plan.data)
        self.assertIn(b'stealth-logo-trigger', res_plan.data)
        res_plan.close()

        # Private
        res_priv = self.client.get('/private.html')
        self.assertEqual(res_priv.status_code, 200)
        self.assertIn(b'Good to see you', res_priv.data)
        self.assertIn(b'Quick Exit', res_priv.data)
        res_priv.close()

    def test_static_assets_served(self):
        css_res = self.client.get('/css/base.css')
        self.assertEqual(css_res.status_code, 200)
        self.assertIn(b'--bg-warm', css_res.data)
        css_res.close()

        js_res = self.client.get('/js/api.js')
        self.assertEqual(js_res.status_code, 200)
        self.assertIn(b'API =', js_res.data)
        js_res.close()

        lp_res = self.client.get('/js/longpress.js')
        self.assertEqual(lp_res.status_code, 200)
        self.assertIn(b'HOLD_DURATION', lp_res.data)
        lp_res.close()

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).parents[1] / 'manager'))
import app as manager

class SafetyTests(unittest.TestCase):
    def test_cross_site_post_is_rejected(self):
        c = manager.app.test_client()
        for endpoint in ('/', '/backups/example.tar.gz'):
            self.assertEqual(c.get(endpoint).status_code, 401)
        self.assertEqual(c.post('/update').status_code, 401)
        import secrets, base64
        password = secrets.token_urlsafe()
        auth = patch.object(manager, 'manager_password', return_value=password)
        auth.start()
        self.addCleanup(auth.stop)
        c.environ_base['HTTP_AUTHORIZATION'] = 'Basic ' + base64.b64encode(('admin:' + password).encode()).decode()
        self.assertEqual(c.post('/update').status_code, 400)
        c.get('/')
        with c.session_transaction() as s:
            token = s['_csrf']
        self.assertEqual(c.post('/update', data={'_csrf': token}, headers={'Origin': 'https://foreign.example'}).status_code, 403)

    def test_unmanaged_container_is_preserved(self):
        d = Mock()
        d.containers.get.return_value.labels = {}
        with self.assertRaises(RuntimeError):
            manager.owned_container(d, 'teslamate-qnap-database')
        d.containers.get.return_value.remove.assert_not_called()

    def test_invalid_ports_and_major_migration(self):
        cfg = dict(manager.DEFAULTS)
        cfg['grafana_port'] = cfg['teslamate_port']
        with self.assertRaises(ValueError): manager.validate_config(cfg)
        cfg = dict(manager.DEFAULTS)
        cfg['postgres_image'] = 'postgres:19-trixie'
        with self.assertRaises(ValueError): manager.validate_config(cfg, manager.DEFAULTS)

    def test_official_defaults_are_valid(self):
        manager.validate_config(manager.DEFAULTS)

if __name__ == '__main__': unittest.main()

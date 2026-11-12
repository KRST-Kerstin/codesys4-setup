import hashlib
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from scripts import install_verified_package as installer


class InstallSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.payload = b'fixture deb bytes'
        self.manifest = self.root / 'release.json'
        self.release = {'version': '1.0.0.0', 'url': 'https://fixture.invalid/package.deb',
                        'sha256': hashlib.sha256(self.payload).hexdigest()}
        self.manifest.write_text(json.dumps(self.release))
        self.cache = self.root / 'cache'
        self.args = ['--manifest', str(self.manifest), '--cache-dir', str(self.cache), '--version', '1.0.0.0']

    def tearDown(self):
        self.temp.cleanup()

    def run_installer(self, urlopen, run):
        with patch('sys.argv', ['installer', *self.args]), patch.object(installer.urllib.request, 'urlopen', urlopen), patch.object(installer.subprocess, 'run', run):
            return installer.main()

    def test_network_failure_never_invokes_package_tools(self):
        from urllib.error import URLError
        with self.assertRaises(URLError):
            self.run_installer(lambda *a, **k: (_ for _ in ()).throw(URLError('offline')), lambda *a, **k: self.fail('package tool invoked'))

    def test_hash_mismatch_never_invokes_package_tools(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return b'not the approved package'
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            self.run_installer(lambda *a, **k: Response(), lambda *a, **k: self.fail('package tool invoked'))

    def test_invalid_deb_never_invokes_apt(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(inner): return self.payload
        calls = []
        def run(command, **kwargs):
            calls.append(command[0])
            if command[0] == 'dpkg-deb':
                raise installer.subprocess.CalledProcessError(2, command)
        with self.assertRaises(installer.subprocess.CalledProcessError):
            self.run_installer(lambda *a, **k: Response(), run)
        self.assertEqual(calls, ['dpkg-deb'])

    def test_wrong_cached_content_is_rejected_before_package_tools(self):
        self.cache.mkdir()
        identity = hashlib.sha256(f"{self.release['version']}\0{self.release['url']}\0{self.release['sha256']}".encode()).hexdigest()
        (self.cache / f"{self.release['version']}-{identity}.deb").write_bytes(b'wrong cache content')
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            self.run_installer(lambda *a, **k: self.fail('cache should not be downloaded over'), lambda *a, **k: self.fail('package tool invoked'))

    def test_success_checks_archive_before_install_and_revalidates_cache(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(inner): return self.payload
        calls = []
        def run(command, **kwargs): calls.append(command[0])
        self.run_installer(lambda *a, **k: Response(), run)
        self.assertEqual(calls, ['dpkg-deb', 'sudo', 'sudo'])
        calls.clear()
        self.run_installer(lambda *a, **k: self.fail('valid cache should be reused'), run)
        self.assertEqual(calls, ['dpkg-deb', 'sudo', 'sudo'])


if __name__ == '__main__':
    unittest.main()

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_manifest", ROOT / "scripts" / "validate_release_manifest.py")
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReleaseManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / "releases" / "codesys4-linux-amd64.json").read_text())

    def test_accepts_approved_release_record(self):
        self.assertEqual(module.validate(self.manifest), self.manifest)

    def test_rejects_missing_or_malformed_required_fields(self):
        invalid_values = {
            "version": "", "architecture": "arm64", "url": "", "sha256": "not-a-hash",
            "provenance": "", "artifact_scope": "", "reviewed_at": "bad-date",
        }
        for key, value in invalid_values.items():
            with self.subTest(field=key):
                broken = dict(self.manifest)
                broken[key] = value
                with self.assertRaises(ValueError):
                    module.validate(broken)
        for key in invalid_values:
            with self.subTest(missing=key):
                broken = dict(self.manifest)
                del broken[key]
                with self.assertRaises(ValueError):
                    module.validate(broken)

    def test_rejects_unpinned_version_url_or_architecture(self):
        for key, value in (("version", "2.0"), ("url", "https://example.invalid/file.deb"), ("architecture", "arm64")):
            with self.subTest(field=key):
                broken = dict(self.manifest, **{key: value})
                with self.assertRaises(ValueError):
                    module.validate(broken)


if __name__ == "__main__":
    unittest.main()

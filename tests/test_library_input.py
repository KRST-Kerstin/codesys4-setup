"""Offline tests for the intentionally empty library input contract."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_library_input.py"


class LibraryInputTests(unittest.TestCase):
    def validate(self, value):
        return subprocess.run(
            [sys.executable, str(VALIDATOR)],
            env={"PATH": __import__("os").environ["PATH"], "LIBRARY_IDS": value},
            capture_output=True,
            text=True,
        )

    def test_default_empty_list_succeeds(self):
        result = self.validate("")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("no libraries", result.stdout.lower())

    def test_any_requested_library_fails_clearly_as_unsupported(self):
        result = self.validate("Standard@3.5.18.0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not implemented", result.stderr.lower())

    def test_wildcard_latest_is_rejected_without_resolution(self):
        for value in ("Standard@latest", "Standard@*"):
            with self.subTest(value=value):
                result = self.validate(value)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("wildcard/latest", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()

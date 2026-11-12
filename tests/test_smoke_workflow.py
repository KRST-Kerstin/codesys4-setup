"""Offline contract checks for the repository's GitHub Actions smoke workflow."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "smoke.yml"


class SmokeWorkflowTests(unittest.TestCase):
    def test_static_validation_runs_on_push_and_pull_request(self):
        text = WORKFLOW.read_text()
        self.assertRegex(text, r"(?m)^  push:\s*$")
        self.assertRegex(text, r"(?m)^  pull_request:\s*$")
        self.assertIn("validate-workflow", text)
        self.assertIn("python3 -m unittest", text)

    def test_binary_smoke_is_explicitly_opt_in_and_manually_triggered(self):
        text = WORKFLOW.read_text()
        self.assertRegex(text, r"(?m)^  workflow_dispatch:\s*$")
        self.assertRegex(text, r"(?m)^      run_codesys_smoke:\s*$")
        self.assertRegex(text, r"(?m)^    if: .*inputs\.run_codesys_smoke.*true")
        self.assertRegex(text, r"(?m)^        uses: \.\/\s*$")
        self.assertRegex(text, r"(?m)^        run: c4-cli version\s*$")
        self.assertIn("Store/EULA terms", text)
        self.assertIn("does not test PLC builds, UI, or TLS", text)

    def test_workflow_has_no_external_download_login_or_secret(self):
        text = WORKFLOW.read_text()
        self.assertNotRegex(text, r"(?i)\b(curl|wget|docker|password|token|secret)\b")


if __name__ == "__main__":
    unittest.main()

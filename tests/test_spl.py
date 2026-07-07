import json
from pathlib import Path
import subprocess
import sys
import unittest

from reference_engine.policy import RuntimePolicy
from reference_engine.spl import SPL_VERSION, compile_spl, compile_spl_file


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "policies" / "github_actions_shadow_spl.json"


class SPLTests(unittest.TestCase):
    def test_example_compiles_to_runtime_policy(self):
        policy = compile_spl_file(EXAMPLE)

        self.assertIsInstance(policy, RuntimePolicy)
        self.assertEqual(policy.tenant_id, "platform-team")
        self.assertEqual(policy.policy_id, "github-actions-shadow-mode")
        self.assertEqual(policy.mode, "OBSERVE")
        self.assertEqual(policy.evidence_ceiling, "OBSERVE")
        self.assertEqual(len(policy.policy_hash), 64)

    def test_unknown_fields_and_wrong_version_are_rejected(self):
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["surprise"] = True
        with self.assertRaisesRegex(ValueError, "unknown field"):
            compile_spl(payload)

        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["version"] = "smerc.spl.v99"
        with self.assertRaisesRegex(ValueError, SPL_VERSION):
            compile_spl(payload)

    def test_spl_cannot_bypass_runtime_policy_safety(self):
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["policy"]["mode"] = "ENFORCE"
        payload["policy"]["fail_behavior"] = "report_unavailable"
        payload["evidence"]["ceiling"] = "CALIBRATED_ENFORCE"

        with self.assertRaisesRegex(ValueError, "ENFORCE mode requires fail_closed"):
            compile_spl(payload)

        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["policy"]["mode"] = "ENFORCE"
        payload["policy"]["fail_behavior"] = "fail_closed"
        payload["evidence"]["ceiling"] = "OBSERVE"

        with self.assertRaisesRegex(ValueError, "exceeds evidence ceiling"):
            compile_spl(payload)

    def test_cli_outputs_compiled_policy_and_hash(self):
        pretty = subprocess.run(
            [sys.executable, "-m", "reference_engine.spl", str(EXAMPLE), "--pretty"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        compiled = json.loads(pretty.stdout)
        self.assertEqual(compiled["version"], "smerc.policy.v1")
        self.assertEqual(compiled["tenant_id"], "platform-team")

        digest = subprocess.run(
            [sys.executable, "-m", "reference_engine.spl", str(EXAMPLE), "--hash"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertRegex(digest.stdout.strip(), r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()


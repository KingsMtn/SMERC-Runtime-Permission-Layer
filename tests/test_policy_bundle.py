import copy
import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.policy_bundle import (
    BUNDLE_SIGNATURE_VERSION,
    build_policy_bundle,
    render_policy_bundle_markdown,
    sign_policy_bundle,
    verify_policy_bundle,
    write_policy_bundle_outputs,
)
from reference_engine.spl import compile_spl_file


ROOT = Path(__file__).resolve().parents[1]
SIGNING_KEY = "local-policy-bundle-signing-key-012345"


class PolicyBundleTests(unittest.TestCase):
    def test_signed_bundle_binds_policy_artifacts_and_approval(self):
        bundle = build_policy_bundle(
            bundle_id="github-actions-shadow-mode-2026-07-07",
            tenant_id="platform-team",
            spl_path=ROOT / "examples" / "policies" / "github_actions_shadow_spl.json",
            artifact_paths=[
                {"type": "domain_profile", "path": ROOT / "examples" / "domain_profiles" / "github_actions_strict.json"},
                {"type": "control_mapping", "path": ROOT / "examples" / "control_mapping" / "github_actions_controls.json"},
            ],
            approved_by="security-architecture-review",
            approved_at="2026-07-07T00:00:00Z",
            change_ticket="SMERC-PILOT-001",
            generated_at="2026-08-02T00:00:00Z",
        )
        signed = sign_policy_bundle(bundle, SIGNING_KEY, key_id="pilot-policy-key-1")

        self.assertTrue(signed["verification"]["valid"])
        self.assertEqual(signed["signature"]["version"], BUNDLE_SIGNATURE_VERSION)
        self.assertEqual(signed["policy"]["policy_id"], "github-actions-shadow-mode")
        self.assertEqual(signed["approval"]["activation_gate"], "policy bundle must verify before runtime activation")
        self.assertEqual([item["type"] for item in signed["artifacts"]], ["spl", "domain_profile", "control_mapping"])

        verified = verify_policy_bundle(signed, signing_key=SIGNING_KEY, root=ROOT)
        self.assertTrue(verified["valid"])
        self.assertTrue(verified["signature_checked"])

    def test_bundle_detects_tampering_and_wrong_signature_key(self):
        bundle = sign_policy_bundle(
            build_policy_bundle(
                bundle_id="github-actions-shadow-mode-2026-07-07",
                tenant_id="platform-team",
                spl_path=ROOT / "examples" / "policies" / "github_actions_shadow_spl.json",
                approved_by="security-architecture-review",
                approved_at="2026-07-07T00:00:00Z",
                change_ticket="SMERC-PILOT-001",
                generated_at="2026-08-02T00:00:00Z",
            ),
            SIGNING_KEY,
        )
        tampered = copy.deepcopy(bundle)
        tampered["policy"]["mode"] = "ENFORCE"

        verification = verify_policy_bundle(tampered, signing_key=SIGNING_KEY, root=ROOT)
        self.assertFalse(verification["valid"])
        self.assertIn("bundle digest mismatch", verification["errors"])
        self.assertIn("signature digest mismatch", verification["errors"])

        wrong_key = verify_policy_bundle(bundle, signing_key="wrong-policy-bundle-signing-key-012345", root=ROOT)
        self.assertFalse(wrong_key["valid"])
        self.assertIn("signature mismatch", wrong_key["errors"])

    def test_mismatched_runtime_policy_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            compiled = compile_spl_file(ROOT / "examples" / "policies" / "github_actions_shadow_spl.json").to_dict()
            compiled["policy_revision"] = "different"
            path.write_text(json.dumps(compiled), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "runtime_policy_path"):
                build_policy_bundle(
                    bundle_id="bad-bundle",
                    tenant_id="platform-team",
                    spl_path=ROOT / "examples" / "policies" / "github_actions_shadow_spl.json",
                    runtime_policy_path=path,
                    approved_by="security-architecture-review",
                    approved_at="2026-07-07T00:00:00Z",
                    change_ticket="SMERC-PILOT-001",
                )

    def test_output_writers_and_docs_exist(self):
        bundle = sign_policy_bundle(
            build_policy_bundle(
                bundle_id="github-actions-shadow-mode-2026-07-07",
                tenant_id="platform-team",
                spl_path=ROOT / "examples" / "policies" / "github_actions_shadow_spl.json",
                approved_by="security-architecture-review",
                approved_at="2026-07-07T00:00:00Z",
                change_ticket="SMERC-PILOT-001",
                generated_at="2026-08-02T00:00:00Z",
            ),
            SIGNING_KEY,
        )
        markdown = render_policy_bundle_markdown(bundle)
        self.assertIn("SMERC Policy Bundle Manifest", markdown)
        self.assertIn("does not replace customer change-management", markdown)

        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "bundle.json"
            markdown_path = Path(directory) / "bundle.md"
            write_policy_bundle_outputs(bundle, json_path=json_path, markdown_path=markdown_path)
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())

        doc = (ROOT / "docs" / "Policy_Bundle_Manifest.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("policy bundle manifests", doc)
        self.assertIn("Policy_Bundle_Manifest.md", readme)


if __name__ == "__main__":
    unittest.main()

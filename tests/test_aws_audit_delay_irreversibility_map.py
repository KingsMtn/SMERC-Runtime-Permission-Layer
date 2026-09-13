import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "examples" / "aws_audit_delay_irreversibility_map.json"


class AWSAuditDelayIrreversibilityMapTests(unittest.TestCase):
    def test_map_contains_pending_state_cache_and_structural_rules(self):
        payload = json.loads(MAP.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["schema_version"],
            "smerc.aws_audit_delay_irreversibility_map.v1",
        )
        self.assertIn("no live AWS data", payload["source_boundary"])
        self.assertEqual(payload["pending_state_cache"]["ttl_minutes"], 30)
        self.assertIn("PENDING_CLOUD_EVIDENCE", payload["pending_state_cache"]["statuses"])
        self.assertEqual(len(payload["structural_irreversibility_rules"]), 6)

    def test_rules_cover_aws_dead_end_and_audit_blinding_actions(self):
        payload = json.loads(MAP.read_text(encoding="utf-8"))
        rules = {rule["rule_id"]: rule for rule in payload["structural_irreversibility_rules"]}

        self.assertIn("kms:DisableKey", rules["AWS-IRR-001"]["aws_action_patterns"])
        self.assertIn("kms:ScheduleKeyDeletion", rules["AWS-IRR-001"]["aws_action_patterns"])
        self.assertEqual(rules["AWS-IRR-001"]["default_smerc_posture"], "DENY")
        self.assertIn("AWS_KMS_RECOVERY_DEAD_END", rules["AWS-IRR-001"]["reason_codes"])

        self.assertIn("cloudtrail:StopLogging", rules["AWS-IRR-002"]["aws_action_patterns"])
        self.assertIn("cloudtrail:DeleteTrail", rules["AWS-IRR-002"]["aws_action_patterns"])
        self.assertEqual(rules["AWS-IRR-002"]["default_smerc_posture"], "FREEZE")
        self.assertIn("AWS_AUDIT_PATH_BLINDING_RISK", rules["AWS-IRR-002"]["reason_codes"])

        self.assertIn("iam:PutRolePermissionsBoundary", rules["AWS-IRR-003"]["aws_action_patterns"])
        self.assertEqual(rules["AWS-IRR-003"]["default_smerc_posture"], "ESCALATE")
        self.assertIn("AWS_PENDING_MUTATION_UNRECONCILED", rules["AWS-IRR-006"]["reason_codes"])

    def test_docs_and_indexing_link_map(self):
        doc = (ROOT / "docs" / "AWS_Audit_Delay_And_Irreversibility_Map.md").read_text(
            encoding="utf-8"
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(
            encoding="utf-8"
        )
        ai_bundle = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(
            encoding="utf-8"
        )
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("Pending State Cache", doc)
        self.assertIn("Structural Irreversibility Rules", doc)
        self.assertIn("examples/aws_audit_delay_irreversibility_map.json", doc)
        self.assertIn("KMS key disable", doc)
        self.assertIn("CloudTrail stop", doc)
        self.assertIn("This map does not call AWS APIs", doc)
        self.assertIn("docs/AWS_Audit_Delay_And_Irreversibility_Map.md", readme)
        self.assertIn("docs/AWS_Audit_Delay_And_Irreversibility_Map.md", indexing)
        self.assertIn("AWS Audit Delay and Irreversibility Map", ai_bundle)
        self.assertIn("AWS audit-delay and irreversibility map", changelog)


if __name__ == "__main__":
    unittest.main()

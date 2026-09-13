import unittest
from pathlib import Path

from reference_engine.aws_audit_delay_irreversibility_replay import (
    build_report,
    load_map,
    normalize_map,
    render_markdown,
)
from reference_engine.aws_pending_mutation_cache import PendingMutationCache, build_cache_from_map


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "examples" / "aws_audit_delay_irreversibility_map.json"


class AWSAuditDelayIrreversibilityReplayTests(unittest.TestCase):
    def test_pending_mutation_cache_constrains_next_action(self):
        cache = PendingMutationCache(ttl_minutes=30)
        cache.record_mutation(
            {
                "permit_id": "permit-test",
                "agent_id": "aws-agent-runtime",
                "workflow_id": "aws-audit-delay-loop",
                "issued_at": "2026-09-12T00:00:00+00:00",
                "expires_at": "2026-09-12T00:30:00+00:00",
                "reconciliation_status": "PENDING_CLOUD_EVIDENCE",
                "pending_mutations": ["cloudtrail:StopLogging"],
                "unreconciled_risk": 0.9,
                "required_evidence": ["replacement trail verified"],
                "reason_codes": ["AWS_AUDIT_PATH_BLINDING_RISK"],
            }
        )

        effect = cache.next_action_effect(agent_id="aws-agent-runtime")

        self.assertEqual(effect["posture_hint"], "FREEZE")
        self.assertIn("AWS_PENDING_MUTATION_UNRECONCILED", effect["reason_codes"])
        self.assertEqual(effect["summary"]["active_unreconciled_count"], 1)

    def test_normalizes_six_rules_into_customer_evaluation_actions(self):
        payload = load_map(MAP)
        normalized = normalize_map(payload)

        self.assertEqual(normalized["version"], "smerc.customer-evaluation.v1")
        self.assertEqual(len(normalized["actions"]), 6)
        self.assertIn("Metadata-only AWS-style replay", normalized["data_boundary"])
        self.assertIn("pending mutation cache", normalized["workflow_context"])

    def test_builds_replay_report_with_cache_and_ledgers(self):
        report = build_report(load_map(MAP))

        self.assertEqual(report["version"], "smerc.aws-audit-delay-irreversibility-replay.v1")
        self.assertEqual(report["rule_count"], 6)
        self.assertEqual(report["normalized_action_count"], 6)
        self.assertEqual(report["valid_dll_ledgers"], 6)
        self.assertEqual(report["pending_mutation_cache"]["active_unreconciled_count"], 6)
        self.assertIn("AWS_PENDING_MUTATION_UNRECONCILED", report["next_action_effect"]["reason_codes"])
        self.assertNotIn("ALLOW", report["smerc_posture_counts"])
        self.assertGreaterEqual(len(report["smerc_posture_counts"]), 2)

    def test_specific_aws_rules_are_not_allowed(self):
        report = build_report(load_map(MAP))
        by_rule = {item["rule_id"]: item for item in report["deltas"]}

        self.assertNotEqual(by_rule["AWS-IRR-001"]["smerc_posture"], "ALLOW")
        self.assertEqual(by_rule["AWS-IRR-001"]["expected_posture"], "DENY")
        self.assertNotEqual(by_rule["AWS-IRR-006"]["smerc_posture"], "ALLOW")
        self.assertIn(by_rule["AWS-IRR-006"]["governance_route"], {"PAUSE", "REVIEW_REQUIRED", "CONSTRAINED_EXECUTE"})

    def test_cache_from_map_records_all_rules(self):
        cache = build_cache_from_map(load_map(MAP))
        summary = cache.summary(agent_id="aws-agent-runtime")

        self.assertEqual(summary["active_unreconciled_count"], 6)
        self.assertIn("AWS_KMS_RECOVERY_DEAD_END", summary["reason_code_counts"])

    def test_markdown_and_docs_reference_runnable_replay(self):
        markdown = render_markdown(build_report(load_map(MAP)))
        doc = (ROOT / "docs" / "AWS_Audit_Delay_And_Irreversibility_Map.md").read_text(encoding="utf-8")

        self.assertIn("AWS Audit Delay And Irreversibility Replay Report", markdown)
        self.assertIn("Pending Mutation Cache", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("python -m reference_engine.aws_audit_delay_irreversibility_replay", doc)
        self.assertIn("reports/AWS_Audit_Delay_And_Irreversibility_Replay_Report.md", doc)


if __name__ == "__main__":
    unittest.main()

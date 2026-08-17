import copy
import unittest
from pathlib import Path

from reference_engine.runtime_evidence_trust import (
    build_runtime_evidence_trust_report,
    evaluate_runtime_evidence_trust,
)


ROOT = Path(__file__).resolve().parents[1]


def _examples():
    import json

    return json.loads((ROOT / "examples" / "runtime_evidence_trust_examples.json").read_text(encoding="utf-8"))


class RuntimeEvidenceTrustTests(unittest.TestCase):
    def test_trusted_github_runtime_evidence_can_support_allow(self):
        scenario = _examples()["scenarios"][0]

        report = evaluate_runtime_evidence_trust(scenario)

        self.assertEqual(report["trust_level"], "HIGH")
        self.assertTrue(report["admissible_for_runtime_decision"])
        self.assertEqual(report["max_recommended_posture"], "ALLOW")
        self.assertEqual(report["missing_required_fields"], [])
        self.assertIn("RUNTIME_EVIDENCE_TRUST_HIGH", report["reason_codes"])

    def test_mixed_mcp_evidence_is_capped_below_allow(self):
        scenario = _examples()["scenarios"][1]

        report = evaluate_runtime_evidence_trust(scenario)

        self.assertEqual(report["trust_level"], "LOW")
        self.assertFalse(report["admissible_for_runtime_decision"])
        self.assertEqual(report["max_recommended_posture"], "FREEZE")
        self.assertIn("HIGH_IMPACT_METADATA_SELF_REPORTED", report["reason_codes"])
        self.assertIn("reversibility", report["high_impact_self_reported_fields"])

    def test_agent_self_reported_high_impact_metadata_is_untrusted_or_low(self):
        scenario = _examples()["scenarios"][2]

        report = evaluate_runtime_evidence_trust(scenario)

        self.assertIn(report["trust_level"], {"LOW", "UNTRUSTED"})
        self.assertIn(report["max_recommended_posture"], {"FREEZE", "DENY"})
        self.assertIn("do_not_allow_based_on_agent_self_description", report["required_controls"])
        self.assertIn("STALE_RUNTIME_EVIDENCE", report["reason_codes"])

    def test_unknown_observed_field_source_is_rejected(self):
        scenario = copy.deepcopy(_examples()["scenarios"][0])
        scenario["observed_fields"]["actor"] = "missing_source"

        with self.assertRaises(ValueError):
            evaluate_runtime_evidence_trust(scenario)

    def test_batch_report_summarizes_trust_levels(self):
        report = build_runtime_evidence_trust_report(_examples())

        self.assertEqual(report["scenario_count"], 3)
        self.assertIn("HIGH", report["trust_level_counts"])
        self.assertGreaterEqual(report["capped_posture_count"], 2)
        self.assertIn("Runtime Evidence Trust Gate Report", report["markdown_report"])

    def test_readme_links_runtime_evidence_trust_gate(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/Runtime_Evidence_Trust_Gate.md", readme)


if __name__ == "__main__":
    unittest.main()

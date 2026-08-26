from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from reference_engine.content_evidence import build_content_evidence_report, evaluate_content_evidence


ROOT = Path(__file__).resolve().parents[1]


def _examples():
    return json.loads((ROOT / "examples" / "content_evidence_examples.json").read_text(encoding="utf-8"))


class ContentEvidenceTests(unittest.TestCase):
    def test_destructive_sql_content_caps_release(self) -> None:
        result = evaluate_content_evidence(_examples()["scenarios"][0])

        self.assertEqual(result["max_recommended_posture"], "DENY")
        self.assertIn("destructive_database_operation", result["high_risk_findings"])
        self.assertIn("CONTENT_RISK_HIGH", result["reason_codes"])

    def test_low_risk_content_can_support_allow(self) -> None:
        result = evaluate_content_evidence(_examples()["scenarios"][2])

        self.assertEqual(result["max_recommended_posture"], "ALLOW")
        self.assertIn("CONTENT_EVIDENCE_ACCEPTABLE", result["reason_codes"])

    def test_scanner_unavailable_freezes_high_impact_content(self) -> None:
        result = evaluate_content_evidence(_examples()["scenarios"][3])

        self.assertEqual(result["max_recommended_posture"], "FREEZE")
        self.assertIn("CONTENT_SCANNER_UNAVAILABLE", result["reason_codes"])
        self.assertIn("AGENT_SUPPLIED_CONTENT_EVIDENCE", result["reason_codes"])

    def test_stale_content_evidence_is_reported(self) -> None:
        result = evaluate_content_evidence(_examples()["scenarios"][4])

        self.assertIn("STALE_CONTENT_EVIDENCE", result["reason_codes"])
        self.assertIn(result["max_recommended_posture"], {"ESCALATE", "DENY"})

    def test_duplicate_assessment_source_is_rejected(self) -> None:
        scenario = copy.deepcopy(_examples()["scenarios"][2])
        scenario["assessments"][1]["source"] = scenario["assessments"][0]["source"]

        with self.assertRaises(ValueError):
            evaluate_content_evidence(scenario)

    def test_report_renders_markdown_and_boundary(self) -> None:
        report = build_content_evidence_report(_examples())

        self.assertEqual(report["scenario_count"], 5)
        self.assertIn("Content Evidence Adapter Report", report["markdown_report"])
        self.assertIn("do not send raw source code", report["evidence_boundary"])


if __name__ == "__main__":
    unittest.main()


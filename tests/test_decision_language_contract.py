import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTURES = {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"}
ROUTE_BY_POSTURE = {
    "ALLOW": "EXECUTE",
    "THROTTLE": "CONSTRAINED_EXECUTE",
    "FREEZE": "PAUSE",
    "DENY": "BLOCK",
    "ESCALATE": "REVIEW_REQUIRED",
}


class DecisionLanguageContractTests(unittest.TestCase):
    def test_decision_schema_exposes_ecosystem_fields(self):
        schema = json.loads((ROOT / "schemas" / "smerc-decision-language-v1.schema.json").read_text(encoding="utf-8"))
        properties = schema["properties"]

        for field in [
            "route_state",
            "required_controls",
            "recoverability",
            "evidence_expectation",
            "postcondition_expectation",
        ]:
            self.assertIn(field, properties)

        self.assertEqual(set(properties["posture"]["enum"]), POSTURES)

    def test_beacon_schema_exists_and_matches_reference_manifest(self):
        schema = json.loads((ROOT / "schemas" / "smerc-beacon-v1.schema.json").read_text(encoding="utf-8"))
        beacon = json.loads((ROOT / "examples" / "smerc_beacon.json").read_text(encoding="utf-8"))

        self.assertEqual(schema["properties"]["schema_version"]["const"], "smerc.beacon.v1")
        for field in schema["required"]:
            self.assertIn(field, beacon)
        self.assertIn("decision_language", beacon)
        self.assertEqual(beacon["decision_language"]["version"], "smerc.decision.v1")

    def test_examples_cover_every_posture_with_route_and_evidence_contract(self):
        examples = sorted((ROOT / "examples" / "decision_language").glob("*_decision.json"))
        self.assertEqual({path.stem.replace("_decision", "").upper() for path in examples}, POSTURES)

        seen = set()
        for path in examples:
            payload = json.loads(path.read_text(encoding="utf-8"))
            posture = payload["posture"]
            seen.add(posture)

            self.assertEqual(payload["language_version"], "smerc.decision.v1")
            self.assertEqual(payload["action_language_version"], "smerc.action.v1")
            self.assertRegex(payload["action_hash"], r"^[a-f0-9]{64}$")
            self.assertEqual(payload["route_state"], ROUTE_BY_POSTURE[posture])
            self.assertTrue(payload["required_controls"])
            self.assertTrue(payload["structured_controls"])
            self.assertTrue(payload["reasons"])
            self.assertIn("rollback_ready", payload["recoverability"])
            self.assertIn("blast_radius_bounded", payload["recoverability"])
            self.assertIn("evidence_sufficient", payload["recoverability"])
            self.assertIn("pre_execution", payload["evidence_expectation"])
            self.assertIn("postcondition", payload["evidence_expectation"])
            self.assertTrue(payload["postcondition_expectation"]["must_preserve_replay"])
            self.assertTrue(payload["postcondition_expectation"]["must_report_missing_controls"])
            self.assertIn("eligible_target_posture", payload["transition"])
            self.assertIn("requires_new_request", payload["transition"])

        self.assertEqual(seen, POSTURES)

    def test_decision_language_doc_is_standards_credible_not_overclaimed(self):
        doc = (ROOT / "docs" / "SMERC_Decision_Language.md").read_text(encoding="utf-8")
        self.assertIn("candidate machine-readable contract", doc)
        self.assertIn("not a government standard", doc)
        self.assertIn("The SMERC engine is one implementation", doc)


if __name__ == "__main__":
    unittest.main()

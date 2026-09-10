import json
import unittest
from pathlib import Path

from reference_engine.decision_language_conformance import check_decision
from reference_engine.decision_language_emitter import emit_decision, load_payload, write_decision


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "decision_language_inputs" / "external_framework_action.json"


class DecisionLanguageEmitterTests(unittest.TestCase):
    def test_emits_conformant_decision_from_external_framework_summary(self):
        decision = emit_decision(load_payload(EXAMPLE))
        conformance = check_decision(decision)

        self.assertEqual(decision["language_version"], "smerc.decision.v1")
        self.assertEqual(decision["action_id"], "external-framework-cloud-change-001")
        self.assertEqual(decision["posture"], "THROTTLE")
        self.assertEqual(decision["route_state"], "CONSTRAINED_EXECUTE")
        self.assertIn("require_rollback_plan", decision["required_controls"])
        self.assertEqual(conformance["status"], "pass")

    def test_rejects_invalid_external_scores(self):
        payload = load_payload(EXAMPLE)
        payload["risk"]["irreversible_exposure"] = 1.2

        with self.assertRaises(ValueError):
            emit_decision(payload)

    def test_writes_output_for_reviewer_use(self):
        scratch = ROOT / "tests" / "_tmp" / "decision_language_emitter"
        scratch.mkdir(parents=True, exist_ok=True)
        output = scratch / "external_framework_smerc_decision.json"

        decision = emit_decision(load_payload(EXAMPLE))
        write_decision(decision, output)
        written = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(written["posture"], "THROTTLE")
        self.assertEqual(check_decision(written)["status"], "pass")

    def test_docs_and_readme_reference_implementer_quickstart(self):
        doc = (ROOT / "docs" / "SMERC_Decision_Language_Implementer_Quickstart.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("external agent framework", doc)
        self.assertIn("decision_language_emitter", doc)
        self.assertIn("SMERC_Decision_Language_Implementer_Quickstart.md", readme)


if __name__ == "__main__":
    unittest.main()

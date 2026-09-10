import copy
import json
import unittest
from pathlib import Path

from reference_engine.decision_language_conformance import (
    build_conformance_report,
    check_decision,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = ROOT / "examples" / "decision_language"


class DecisionLanguageConformanceTests(unittest.TestCase):
    def test_examples_pass_conformance_for_all_postures(self):
        paths = sorted(EXAMPLE_DIR.glob("*_decision.json"))
        report = build_conformance_report(paths)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["decision_count"], 5)
        self.assertEqual(set(report["posture_counts"]), {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"})
        self.assertEqual(report["status_counts"], {"pass": 5})

    def test_detects_route_and_transition_mismatch(self):
        payload = json.loads((EXAMPLE_DIR / "deny_decision.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(payload)
        broken["route_state"] = "EXECUTE"
        broken["transition"]["requires_new_request"] = False

        result = check_decision(broken, source="broken-deny")

        self.assertEqual(result["status"], "fail")
        self.assertIn("route_state does not match posture", result["errors"])
        self.assertIn("DENY must require a new request", result["errors"])

    def test_markdown_and_outputs_explain_boundary(self):
        report = build_conformance_report(sorted(EXAMPLE_DIR.glob("*_decision.json")))
        markdown = render_markdown(report)

        self.assertIn("SMERC Decision Language Conformance Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("Evidence Boundary", markdown)

        scratch = ROOT / "tests" / "_tmp" / "decision_language_conformance"
        scratch.mkdir(parents=True, exist_ok=True)
        json_path = scratch / "decision-language-conformance.json"
        markdown_path = scratch / "Decision_Language_Conformance_Report.md"
        write_outputs(report, json_output=json_path, markdown_output=markdown_path)

        self.assertTrue(json_path.exists())
        self.assertTrue(markdown_path.exists())

    def test_docs_and_readme_reference_conformance(self):
        doc = (ROOT / "docs" / "SMERC_Decision_Language_Conformance.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("contract-shape conformance only", doc)
        self.assertIn("reference_engine.decision_language_conformance", doc)
        self.assertIn("SMERC_Decision_Language_Conformance.md", readme)


if __name__ == "__main__":
    unittest.main()

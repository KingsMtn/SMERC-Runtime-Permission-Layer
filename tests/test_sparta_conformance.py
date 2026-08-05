import copy
import json
import unittest
from pathlib import Path

from reference_engine.sparta_conformance import (
    SPARTA_CONFORMANCE_REPORT_VERSION,
    build_conformance_report,
    render_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "examples" / "sparta" / "adapter_registry.json"


class SPARTaConformanceTests(unittest.TestCase):
    def test_registry_conformance_report_checks_every_posture(self):
        report = build_conformance_report(REGISTRY)
        self.assertEqual(report["version"], SPARTA_CONFORMANCE_REPORT_VERSION)
        self.assertEqual(report["summary"]["adapter_count"], 4)
        self.assertEqual(report["summary"]["posture_probe_count"], 20)
        self.assertEqual(report["summary"]["failed_posture_probe_count"], 0)
        self.assertTrue(report["summary"]["passed"])

        adapters = {item["adapter_id"]: item for item in report["adapter_results"]}
        github = adapters["github-actions-deployer"]
        self.assertEqual(self.route_for(github, "THROTTLE")["actual_route_state"], "CONSTRAINED_EXECUTE")

        ticket = adapters["service-ticket-review"]
        self.assertEqual(self.route_for(ticket, "ESCALATE")["actual_route_state"], "REVIEW_REQUIRED")
        self.assertEqual(self.route_for(ticket, "THROTTLE")["actual_route_state"], "REVIEW_REQUIRED")
        self.assertIn("example_adapter_only", report["recommended_next_action"])

    def test_markdown_is_ciso_readable_and_bounded(self):
        markdown = render_markdown(build_conformance_report(REGISTRY))
        self.assertIn("SPARTa Adapter Conformance Report", markdown)
        self.assertIn("not production certification", markdown)
        self.assertIn("github-actions-deployer", markdown)
        self.assertIn("service-ticket-review", markdown)

    def test_conformance_detects_misdeclared_adapter(self):
        source = json.loads(REGISTRY.read_text(encoding="utf-8"))
        altered = copy.deepcopy(source)
        altered["adapters"][0]["supports_scope_limit"] = False
        temp = ROOT / "test_outputs" / "bad_sparta_registry.json"
        temp.parent.mkdir(exist_ok=True)
        temp.write_text(json.dumps(altered), encoding="utf-8")

        report = build_conformance_report(temp)
        self.assertTrue(report["summary"]["passed"])
        github = {item["adapter_id"]: item for item in report["adapter_results"]}["github-actions-deployer"]
        self.assertEqual(self.route_for(github, "THROTTLE")["actual_route_state"], "REVIEW_REQUIRED")
        self.assertIn("scope_limit", github["capability_gaps"])

    @staticmethod
    def route_for(adapter, posture):
        return next(item for item in adapter["posture_results"] if item["posture"] == posture)


if __name__ == "__main__":
    unittest.main()

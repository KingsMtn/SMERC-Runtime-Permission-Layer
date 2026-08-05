import json
import unittest
from pathlib import Path

from reference_engine.fake_customer_pilot import run_fake_customer_pilot


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "examples" / "fake_customer_acme" / "production_like_scenarios.json"
REPORT = ROOT / "reports" / "fake_customer_acme_pilot_report.json"
MARKDOWN = ROOT / "reports" / "Fake_Customer_Acme_Pilot_Report.md"
DOC = ROOT / "docs" / "Fake_Customer_Production_Like_Test.md"


class FakeCustomerPilotTests(unittest.TestCase):
    def test_fake_customer_scenarios_cover_required_paths(self):
        scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        package = run_fake_customer_pilot(scenarios)
        paths = {record["path"] for record in package["records"]}
        self.assertEqual(
            paths,
            {
                "safe_deployment",
                "risky_production_change",
                "destructive_request",
                "escalated_request",
                "failure_rollback",
            },
        )
        route_states = {record["sparta_route_state"] for record in package["records"]}
        self.assertIn("EXECUTE", route_states)
        self.assertIn("CONSTRAINED_EXECUTE", route_states)
        self.assertIn("BLOCK", route_states)
        self.assertIn("REVIEW_REQUIRED", route_states)
        self.assertEqual(package["summary"]["rollback_scenarios"], 1)

    def test_fake_customer_package_preserves_boundary_and_valid_ledgers(self):
        package = run_fake_customer_pilot(json.loads(SCENARIOS.read_text(encoding="utf-8")))
        self.assertTrue(package["customer_simulation"]["not_customer_evidence"])
        self.assertEqual(package["summary"]["valid_ledger_count"], package["summary"]["scenario_count"])
        self.assertIn("incident reduction in customer environments", package["boundary"]["does_not_prove"])
        self.assertTrue(all(ledger["verification"]["valid"] for ledger in package["ledgers"]))

    def test_checked_in_reports_and_docs_exist(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        markdown = MARKDOWN.read_text(encoding="utf-8")
        doc = DOC.read_text(encoding="utf-8")
        self.assertEqual(report["version"], "smerc.fake-customer-pilot.v1")
        self.assertIn("Fake Customer Production-Like Pilot Report", markdown)
        self.assertIn("not customer proof or production certification", markdown)
        self.assertIn("production-like simulation, not production proof", doc)


if __name__ == "__main__":
    unittest.main()

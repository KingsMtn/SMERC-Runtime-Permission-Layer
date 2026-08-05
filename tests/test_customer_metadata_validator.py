import copy
import unittest
from pathlib import Path

from reference_engine.customer_metadata_validator import load_json, validate_customer_metadata


ROOT = Path(__file__).resolve().parents[1]


class CustomerMetadataValidatorTests(unittest.TestCase):
    def test_public_samples_are_not_ready_for_customer_package(self):
        report = validate_customer_metadata(
            checklist=load_json(ROOT / "examples" / "customer_metadata_substitution_checklist.json"),
            prospect_route=load_json(ROOT / "examples" / "core_prospect_route_sample.json"),
            customer_intake=load_json(ROOT / "examples" / "customer_action_intake_sample.json"),
            pilot_handoff=load_json(ROOT / "examples" / "pilot_handoff_checklist.json"),
            pilot_metrics=load_json(ROOT / "examples" / "pilot_metrics_summary_sample.json"),
        )

        self.assertFalse(report["ready_for_customer_package"])
        joined = " ".join(report["blockers"])
        self.assertIn("Public sample organization names", joined)
        self.assertIn("at least 10 metadata-only actions", joined)
        self.assertIn("Sample pilot metrics", joined)

    def test_substituted_metadata_can_pass_without_metrics(self):
        checklist = load_json(ROOT / "examples" / "customer_metadata_substitution_checklist.json")
        for item in checklist["required_confirmations"]:
            item["confirmed"] = True
        route = load_json(ROOT / "examples" / "core_prospect_route_sample.json")
        route["organization"] = "Acme Security Platform"
        intake = load_json(ROOT / "examples" / "customer_action_intake_sample.json")
        intake["organization"] = "Acme Security Platform"
        base_actions = intake["actions"]
        expanded = []
        for index in range(10):
            action = copy.deepcopy(base_actions[index % len(base_actions)])
            action["action_id"] = f"ACME_ACTION_{index:02d}"
            expanded.append(action)
        intake["actions"] = expanded

        report = validate_customer_metadata(
            checklist=checklist,
            prospect_route=route,
            customer_intake=intake,
            pilot_handoff=load_json(ROOT / "examples" / "pilot_handoff_checklist.json"),
        )

        self.assertTrue(report["ready_for_customer_package"])
        self.assertEqual(report["action_count"], 10)
        self.assertEqual(report["blockers"], [])

    def test_review_only_route_blocks_pilot_package(self):
        checklist = load_json(ROOT / "examples" / "customer_metadata_substitution_checklist.json")
        for item in checklist["required_confirmations"]:
            item["confirmed"] = True
        route = load_json(ROOT / "examples" / "core_prospect_route_sample.json")
        route["organization"] = "Acme Security Platform"
        route["workflow_signals"]["reviewer_labels_possible"] = False
        intake = load_json(ROOT / "examples" / "customer_action_intake_sample.json")
        intake["organization"] = "Acme Security Platform"
        intake["actions"] = [
            {**copy.deepcopy(intake["actions"][index % len(intake["actions"])]), "action_id": f"ACME_ACTION_{index:02d}"}
            for index in range(10)
        ]

        report = validate_customer_metadata(
            checklist=checklist,
            prospect_route=route,
            customer_intake=intake,
            pilot_handoff=load_json(ROOT / "examples" / "pilot_handoff_checklist.json"),
        )

        self.assertFalse(report["ready_for_customer_package"])
        self.assertIn("review_only", " ".join(report["blockers"]))

    def test_readme_links_validation_doc(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/Customer_Metadata_Validation.md", readme)


if __name__ == "__main__":
    unittest.main()

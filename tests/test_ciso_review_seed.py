import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.audit_store import AuditStore
from reference_engine.ciso_review_seed import (
    CISO_REVIEW_SEED_VERSION,
    load_actions,
    render_markdown,
    seed_ciso_review,
)
from reference_engine.pilot_evidence_package import build_pilot_evidence_package


ROOT = Path(__file__).resolve().parents[1]
SEED_ACTIONS = ROOT / "examples" / "ciso_review_seed_actions.json"


class CISOReviewSeedTests(unittest.TestCase):
    def test_seed_actions_are_valid_and_realistic(self):
        actions = load_actions(SEED_ACTIONS)
        self.assertEqual(len(actions), 5)
        self.assertEqual(len({action["action_id"] for action in actions}), 5)
        self.assertTrue(any(action["external_side_effect"] for action in actions))
        self.assertTrue(any(action["sensitive_data"] for action in actions))
        self.assertTrue(any(action["context"]["domain_profile"] == "github_actions" for action in actions))

    def test_seed_creates_review_queue_and_evidence_package_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "ciso_seed.sqlite3"
            report = seed_ciso_review(load_actions(SEED_ACTIONS), audit_db=db_path)
            self.assertEqual(report["version"], CISO_REVIEW_SEED_VERSION)
            self.assertEqual(report["seeded_decision_count"], 5)
            postures = {item["posture"] for item in report["seeded_decisions"]}
            self.assertIn("ALLOW", postures)
            self.assertIn("THROTTLE", postures)
            self.assertTrue({"DENY", "ESCALATE"} & postures)

            store = AuditStore(db_path)
            queue = store.review_queue("pilot-team", review_status="pending", limit=10)
            self.assertEqual(len(queue), 5)
            ledgers = store.list_decision_lifecycle_ledgers("pilot-team", limit=10)
            self.assertEqual(len(ledgers), 5)

            first_decision_id = report["seeded_decisions"][0]["dll_decision_id"]
            ledger = store.get_decision_lifecycle_ledger("pilot-team", first_decision_id)
            package = build_pilot_evidence_package(
                ledger,
                generated_by="ciso-review-seed-test",
                security_events=store.list_security_events("pilot-team", limit=20),
            )
            store.close()
            self.assertEqual(package["decision_id"], first_decision_id)
            self.assertTrue(package["certificate_verification"]["valid"])
            self.assertIn("SMERC Pilot Evidence Package", package["markdown_report"])

    def test_report_markdown_states_evidence_boundary(self):
        report = {
            "version": CISO_REVIEW_SEED_VERSION,
            "generated_at": "2026-07-15T12:00:00+00:00",
            "tenant_id": "pilot-team",
            "audit_db": "example.sqlite3",
            "evidence_boundary": "seeded walkthrough data; not customer evidence",
            "next_steps": ["Open the pilot console."],
            "seeded_decisions": [
                {
                    "action_id": "CISO_REVIEW_DEPLOY_CANARY",
                    "posture": "THROTTLE",
                    "replay_id": "replay-1",
                    "dll_decision_id": "dll:ciso-review:ciso_review_deploy_canary",
                }
            ],
        }
        markdown = render_markdown(report)
        self.assertIn("not customer evidence", markdown)
        self.assertIn("CISO_REVIEW_DEPLOY_CANARY", markdown)

    def test_action_file_is_json_array(self):
        payload = json.loads(SEED_ACTIONS.read_text(encoding="utf-8"))
        self.assertIsInstance(payload, list)


if __name__ == "__main__":
    unittest.main()

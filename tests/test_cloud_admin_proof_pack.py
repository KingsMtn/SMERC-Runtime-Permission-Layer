import unittest
from pathlib import Path

from reference_engine.cloud_admin_proof_pack import (
    build_cloud_admin_proof_pack,
    cloud_reason_codes,
    load_payload,
    render_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "cloud_admin_customer_eval_actions.json"


class CloudAdminProofPackTests(unittest.TestCase):
    def test_builds_expanded_cloud_admin_proof_pack(self):
        report = build_cloud_admin_proof_pack(load_payload(SAMPLE))

        self.assertEqual(report["version"], "smerc.cloud-admin-proof-pack.v1")
        self.assertEqual(report["summary"]["total_actions"], 24)
        self.assertEqual(report["summary"]["valid_ledgers"], 24)
        self.assertGreaterEqual(report["summary"]["non_executable_routes"], 3)
        self.assertEqual(report["pilot_fit"]["fit"], "strong")
        self.assertIn("IAM_SCOPE_EXPANSION", report["cloud_reason_code_counts"])
        self.assertIn("ROLLBACK_UNCERTAIN", report["cloud_reason_code_counts"])
        self.assertIn("PRODUCTION_BLAST_RADIUS_WIDE", report["cloud_reason_code_counts"])

    def test_records_include_cloud_reason_codes_and_impact(self):
        report = build_cloud_admin_proof_pack(load_payload(SAMPLE))

        for record in report["records"]:
            self.assertIn("cloud_reason_codes", record)
            self.assertIn("cloud_reason_labels", record)
            self.assertIn("work_result_impact", record)
            self.assertIn("work", record["work_result_impact"])
            self.assertIn("result", record["work_result_impact"])
            self.assertIn("impact", record["work_result_impact"])

    def test_cloud_reason_codes_capture_specific_cloud_risks(self):
        report = build_cloud_admin_proof_pack(load_payload(SAMPLE))
        iam_record = next(record for record in report["records"] if record["action_id"].startswith("CLOUDCO_IAM_EXPANSION_001"))
        delete_record = next(record for record in report["records"] if record["action_id"].startswith("CLOUDCO_DATABASE_DELETE_003"))

        self.assertIn("IAM_SCOPE_EXPANSION", iam_record["cloud_reason_codes"])
        self.assertIn("DATA_PLANE_DESTRUCTIVE_ACTION", delete_record["cloud_reason_codes"])
        self.assertIn("ROLLBACK_UNCERTAIN", delete_record["cloud_reason_codes"])

    def test_markdown_is_reviewer_readable_and_bounded(self):
        markdown = render_markdown(build_cloud_admin_proof_pack(load_payload(SAMPLE)))

        self.assertIn("Cloud Admin Proof Pack", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("Cloud Reason Codes", markdown)
        self.assertIn("does not connect to AWS", markdown)
        self.assertIn("replacement for IAM", markdown)

    def test_docs_reference_cloud_admin_proof_pack(self):
        doc = (ROOT / "docs" / "Cloud_Admin_Proof_Pack.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.cloud_admin_proof_pack", doc)
        self.assertIn("metadata-only", doc)
        self.assertIn("AWS", doc)


if __name__ == "__main__":
    unittest.main()

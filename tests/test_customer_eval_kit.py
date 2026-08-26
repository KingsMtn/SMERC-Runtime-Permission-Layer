from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CustomerEvalKitTests(unittest.TestCase):
    def test_customer_eval_kit_files_exist(self) -> None:
        required = [
            ROOT / "customer_eval" / "README.md",
            ROOT / "customer_eval" / "20_Minute_Company_Evaluation.md",
            ROOT / "customer_eval" / "package_manifest.json",
            ROOT / "customer_eval" / "reviewer_scorecard.md",
            ROOT / "customer_eval" / "expected_report_outline.md",
        ]
        for path in required:
            with self.subTest(path=str(path)):
                self.assertTrue(path.exists(), f"missing {path}")
                self.assertTrue(path.read_text(encoding="utf-8").strip())

    def test_customer_eval_manifest_references_existing_assets(self) -> None:
        manifest = json.loads((ROOT / "customer_eval" / "package_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "smerc.customer-eval-kit.v1")
        self.assertIn("production safety", manifest["evidence_boundary"])
        self.assertEqual(manifest["primary_workflow"], ".github/workflows/customer-evaluations.yml")
        self.assertTrue((ROOT / manifest["primary_workflow"]).exists())

        for pack in manifest["input_packs"]:
            with self.subTest(pack=pack["id"]):
                self.assertTrue((ROOT / pack["path"]).exists(), pack["path"])

    def test_customer_eval_kit_preserves_safe_boundaries(self) -> None:
        readme = (ROOT / "customer_eval" / "README.md").read_text(encoding="utf-8")
        self.assertIn("metadata-only", readme)
        self.assertIn("secrets", readme)
        self.assertIn("does not prove production safety", readme)
        self.assertIn("enforce-mode readiness", readme)


if __name__ == "__main__":
    unittest.main()

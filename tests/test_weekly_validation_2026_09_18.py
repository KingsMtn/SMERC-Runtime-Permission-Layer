import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "docs" / "Weekly_Validation_2026-09-18.md"


class WeeklyValidationRecordTests(unittest.TestCase):
    def test_validation_record_preserves_results_and_boundaries(self):
        text = VALIDATION.read_text(encoding="utf-8")

        for phrase in (
            "70e4f491acff67c7a3e038e7062f403b3a0c559b",
            "Product tests run in the detached clean worktree: `1027`",
            "Tests in the repository after adding this validation record and its two guard tests: `1029`",
            "Failures: `0`",
            "WinError 10053",
            "ready_for_limited_review",
            "ready_for_limited_aws_review",
            "Evidence bundle: `18` artifacts verified with `0` errors and `0` warnings",
            "`6` supported claims and `3` explicitly unsupported claims",
            "not yet ready for a production-enforcement claim",
            "5 to 25 customer-owned, metadata-only actions",
        ):
            self.assertIn(phrase, text)

    def test_readme_links_validation_record(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/Weekly_Validation_2026-09-18.md", readme)


if __name__ == "__main__":
    unittest.main()

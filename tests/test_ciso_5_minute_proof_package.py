import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "docs" / "CISO_5_Minute_Proof_Package.md"
README = ROOT / "README.md"
EXTERNAL_REVIEW = ROOT / "docs" / "External_Review_Start_Here.md"


class CISOFiveMinuteProofPackageTests(unittest.TestCase):
    def test_package_has_tight_review_path_and_pilot_ask(self):
        text = PACKAGE.read_text(encoding="utf-8")
        self.assertIn("Is recoverability-aware runtime permissioning credible enough", text)
        self.assertIn("Five-Minute Review Path", text)
        self.assertIn("reports/Credibility_Partner_Review_Packet.md", text)
        self.assertIn("docs/GitHub_Actions_Pilot_Operator_Quickstart.md", text)
        self.assertIn("reports/GitHub_Actions_Pilot_Readiness.md", text)
        self.assertIn("30 days", text)
        self.assertIn("The first pilot should not block production workflows.", text)

    def test_package_preserves_evidence_boundary(self):
        text = PACKAGE.read_text(encoding="utf-8")
        self.assertIn("not whether SMERC is production-certified", text)
        self.assertIn("not live customer validation", text)
        self.assertIn("should not be represented as production-certified", text)
        blocked_claims = [
            "proven to reduce incidents",
            "compliance-attested",
            "customer-validated",
        ]
        for claim in blocked_claims:
            self.assertIn(claim, text)

    def test_package_links_to_existing_files(self):
        text = PACKAGE.read_text(encoding="utf-8")
        for relative_path in [
            "docs/Plain_English_Product_Overview.md",
            "reports/Credibility_Partner_Review_Packet.md",
            "docs/GitHub_Actions_Pilot_Operator_Quickstart.md",
            "reports/GitHub_Actions_Pilot_Readiness.md",
            "pilot_package/First_Pilot_Path.md",
        ]:
            self.assertIn(relative_path, text)
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_readme_and_external_review_start_here_reference_package(self):
        readme = README.read_text(encoding="utf-8")
        external = EXTERNAL_REVIEW.read_text(encoding="utf-8")
        self.assertIn("docs/CISO_5_Minute_Proof_Package.md", readme)
        self.assertIn("docs/CISO_5_Minute_Proof_Package.md", external)
        self.assertIn("then `docs/CISO_30_Minute_Review_Package.md`", external)


if __name__ == "__main__":
    unittest.main()

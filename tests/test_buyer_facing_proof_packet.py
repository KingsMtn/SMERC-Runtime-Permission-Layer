import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BuyerFacingProofPacketTests(unittest.TestCase):
    def test_packet_contains_product_proof_path_and_boundaries(self):
        text = (ROOT / "docs" / "Buyer_Facing_Proof_Packet.md").read_text(encoding="utf-8")

        for phrase in [
            "pilot-grade product candidate",
            "metadata-only shadow-mode recoverability review",
            "5 to 25 metadata-only actions",
            "where it will execute",
            "execution boundary can contain failure",
            "docs/Shadow_Mode_Product_Lane.md",
            "reports/pilot_intake/Pilot_Intake_Report.md",
            "Did SMERC find at least one meaningful decision gap",
            "What This Can Prove",
            "What This Does Not Prove",
            "AWS endorsement",
            "replacement of IAM",
            "field-of-use separable",
            "tests.test_cross_path_safety_invariants",
            "strictest posture",
            "docs/Cross_Path_Safety_Invariants.md",
            "docs/AWS_Shadow_Mode_Buyer_Example.md",
            "regression evidence, not proof",
        ]:
            self.assertIn(phrase, text)

    def test_packet_is_linked_from_primary_product_surfaces(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readiness = (ROOT / "docs" / "Product_Readiness_Index.md").read_text(encoding="utf-8")

        for text in [readme, readiness]:
            self.assertIn("docs/Buyer_Facing_Proof_Packet.md", text)

    def test_aws_example_is_reproducible_and_bounded(self):
        text = (ROOT / "docs" / "AWS_Shadow_Mode_Buyer_Example.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for phrase in [
            "examples/aws_customer_metadata_filled_sample.json",
            "reference_engine.aws_metadata_adapter",
            "reports/aws_shadow_mode_buyer_example/AWS_Metadata_Adapter_Report.md",
            "tests.test_cross_path_safety_invariants",
            "five synthetic AWS-style actions",
            "cannot demonstrate deployed AWS enforcement",
        ]:
            self.assertIn(phrase, text)
        self.assertIn("docs/AWS_Shadow_Mode_Buyer_Example.md", readme)


if __name__ == "__main__":
    unittest.main()

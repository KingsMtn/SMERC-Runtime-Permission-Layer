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
        ]:
            self.assertIn(phrase, text)

    def test_packet_is_linked_from_primary_product_surfaces(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readiness = (ROOT / "docs" / "Product_Readiness_Index.md").read_text(encoding="utf-8")

        for text in [readme, readiness]:
            self.assertIn("docs/Buyer_Facing_Proof_Packet.md", text)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALUE_DOC = ROOT / "docs" / "Potential_Company_Value.md"
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"


class PotentialCompanyValueTests(unittest.TestCase):
    def test_value_doc_states_helpful_but_unproven_value(self):
        text = VALUE_DOC.read_text(encoding="utf-8")

        self.assertIn("safely use more automation", text)
        self.assertIn("reduced blast radius", text)
        self.assertIn("safer automation adoption", text)
        self.assertIn("better audit and replay evidence", text)
        self.assertIn("does not claim proven incident reduction", text)

    def test_value_doc_blocks_exaggerated_claims(self):
        text = VALUE_DOC.read_text(encoding="utf-8")

        for phrase in (
            "SMERC reduces incidents.",
            "SMERC prevents outages.",
            "SMERC saves companies millions.",
            "SMERC is better than Microsoft",
            "SMERC is production-certified.",
        ):
            self.assertIn(phrase, text)

        self.assertIn("Do not use", text)
        self.assertIn("Evidence Boundary", text)

    def test_readme_and_changelog_link_value_doc(self):
        self.assertIn("docs/Potential_Company_Value.md", README.read_text(encoding="utf-8"))
        self.assertIn("potential company value", CHANGELOG.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()

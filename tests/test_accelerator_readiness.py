from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AcceleratorReadinessDocsTests(unittest.TestCase):
    def test_accelerator_track_has_evidence_first_boundary(self):
        text = (ROOT / "docs" / "Accelerator_Readiness_Track.md").read_text()

        self.assertIn("pre-execution recoverability control", text)
        self.assertIn("technical review and shadow-mode pilot discussion", text)
        self.assertIn("customer-proven risk reduction", text)
        self.assertIn("Do not claim", text)
        self.assertIn("Open README", text)

    def test_mach37_readiness_stays_narrow_and_skeptical(self):
        text = (ROOT / "docs" / "MACH37_Application_Readiness.md").read_text()

        self.assertIn("GitHub Actions / pull request guardian", text)
        self.assertIn("Why Is This Not Just OPA?", text)
        self.assertIn("Why Is This Not Just An AI Gateway?", text)
        self.assertIn("Do not submit", text)
        self.assertIn("one real external-review signal", text)

    def test_readme_links_accelerator_materials(self):
        text = (ROOT / "README.md").read_text()

        self.assertIn("docs/Accelerator_Readiness_Track.md", text)
        self.assertIn("docs/MACH37_Application_Readiness.md", text)


if __name__ == "__main__":
    unittest.main()

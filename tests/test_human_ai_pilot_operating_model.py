import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "pilot_package" / "Human_AI_Pilot_Operating_Model.md"


class HumanAIPilotOperatingModelTests(unittest.TestCase):
    def test_model_separates_ai_automation_from_human_accountability(self):
        text = MODEL.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertIn("human-supervised ai-action governance", lowered)
        self.assertIn("ai agents, bots, scripts, and workflows may propose actions", lowered)
        self.assertIn("customer humans validate", lowered)
        self.assertIn("ciso or delegate", lowered)
        self.assertIn("owns go/no-go", lowered)

    def test_model_defines_human_only_decisions_and_review_labels(self):
        text = MODEL.read_text(encoding="utf-8")
        self.assertIn("Customer AI should not be the final authority", text)
        self.assertIn("false_release_candidate", text)
        self.assertIn("false_constraint_candidate", text)
        self.assertIn("useful_constraint", text)
        self.assertIn("AI-generated labels can be used as drafts only", text)

    def test_model_preserves_first_pilot_boundary(self):
        text = MODEL.read_text(encoding="utf-8").lower()
        self.assertIn("first pilot", text)
        self.assertIn("observe", text)
        self.assertIn("recommend", text)
        self.assertIn("enforce-readiness", text)
        self.assertIn("should not automate accountability", text)


if __name__ == "__main__":
    unittest.main()


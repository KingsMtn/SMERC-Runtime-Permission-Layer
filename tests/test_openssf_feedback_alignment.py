import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "OpenSSF_Feedback_Alignment.md"


class OpenSSFFeedbackAlignmentTests(unittest.TestCase):
    def test_alignment_note_preserves_hard_gate_before_scoring(self):
        text = DOC.read_text(encoding="utf-8")

        for phrase in [
            "OpenSSF issue #50",
            "Recoverability scoring should not be allowed to rescue",
            "identity and scoped workload session",
            "typed tool/action contract",
            "attested runtime evidence",
            "least-privilege boundary",
            "expected object-shape check",
            "SMERC recoverability posture",
        ]:
            self.assertIn(phrase, text)

    def test_alignment_note_links_implemented_artifacts_and_boundaries(self):
        text = DOC.read_text(encoding="utf-8")

        for phrase in [
            "reference_engine.ref_gated_runtime_proof",
            "reference_engine.customer_evaluation",
            "reference_engine.mcp_governance_gateway",
            "examples/cloud_admin_customer_eval_actions.json",
            "This does not prove",
            "production MCP security",
            "reduction in customer incidents",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from reference_engine.mcp_governance_gateway import load_json
from reference_engine.ref_gated_runtime_proof import (
    REF_GATED_RUNTIME_PROOF_VERSION,
    build_ref_gated_runtime_proof,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "examples" / "mcp" / "governance_gateway_registry.json"
SESSION = ROOT / "examples" / "mcp" / "governance_gateway_session.json"
TEST_OUTPUTS = ROOT / "test_outputs" / "ref_gated_runtime_proof"
TEST_OUTPUTS.mkdir(parents=True, exist_ok=True)


class RefGatedRuntimeProofTests(unittest.TestCase):
    def test_ref_gate_runs_before_scoring_and_routing(self):
        report = build_ref_gated_runtime_proof(registry=load_json(REGISTRY), session=load_json(SESSION))

        self.assertEqual(report["version"], REF_GATED_RUNTIME_PROOF_VERSION)
        self.assertEqual(report["summary"]["request_count"], 4)
        self.assertGreaterEqual(report["summary"]["ref_gate_failure_count"], 1)
        self.assertGreaterEqual(report["summary"]["scoring_capped_count"], 1)
        self.assertIn("Ref gate", report["sequence"][0])

    def test_failed_ref_gate_caps_scoring_and_creates_valid_dll(self):
        report = build_ref_gated_runtime_proof(registry=load_json(REGISTRY), session=load_json(SESSION))
        failed = [item for item in report["proof_items"] if item["ref_gate"]["status"] == "fail"]

        self.assertTrue(failed)
        self.assertEqual(failed[0]["scoring_stage"]["admission"], "capped_by_ref_gate")
        self.assertFalse(failed[0]["sparta_stage"]["executable"])
        self.assertTrue(failed[0]["dll_stage"]["verification"]["valid"])

    def test_passed_ref_gate_can_still_be_constrained_by_smerc(self):
        report = build_ref_gated_runtime_proof(registry=load_json(REGISTRY), session=load_json(SESSION))
        passed = [item for item in report["proof_items"] if item["ref_gate"]["status"] == "pass"]

        self.assertTrue(passed)
        postures = {item["smerc_stage"]["posture"] for item in passed}
        self.assertTrue({"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"} & postures)

    def test_markdown_explains_hard_gates_before_recoverability(self):
        report = build_ref_gated_runtime_proof(registry=load_json(REGISTRY), session=load_json(SESSION))
        markdown = render_markdown(report)
        doc = (ROOT / "docs" / "Ref_Gated_Runtime_Proof_Loop.md").read_text(encoding="utf-8")

        self.assertIn("hard mechanical gates", markdown)
        self.assertIn("recoverability scoring", doc)
        self.assertIn("hard pre-execution controls", doc)

    def test_writes_outputs(self):
        report = build_ref_gated_runtime_proof(registry=load_json(REGISTRY), session=load_json(SESSION))
        json_path = TEST_OUTPUTS / "proof.json"
        markdown_path = TEST_OUTPUTS / "proof.md"
        write_outputs(report, json_path=json_path, markdown_path=markdown_path)
        self.assertTrue(json_path.exists())
        self.assertTrue(markdown_path.exists())


if __name__ == "__main__":
    unittest.main()

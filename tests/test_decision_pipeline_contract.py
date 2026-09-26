import json
import unittest
from copy import deepcopy
from pathlib import Path

from reference_engine.decision_pipeline_contract import VERSION, evaluate_pipeline


ROOT = Path(__file__).resolve().parents[1]


def pipeline(record_index=0):
    manifest = json.loads(
        (ROOT / "examples" / "authorization_afterlife_evidence_manifest.json").read_text(encoding="utf-8")
    )
    manifest["records"] = [manifest["records"][record_index]]
    return {
        "version": VERSION,
        "pipeline_id": f"pipeline-{record_index}",
        "hard_gates": {
            "identity_valid": True,
            "delegation_valid": True,
            "authority_current": True,
            "recovery_capability_present": True,
            "evidence_non_secret": True,
        },
        "action": {
            "action_id": f"action-{record_index}",
            "description": "Bounded metadata-only AWS action",
            "tool": "aws-mcp",
            "actor": "pilot-agent",
            "confidence": 0.95,
            "harm": 0.1,
            "consent": 0.95,
            "reversibility": 0.95,
            "external_effect": False,
            "sensitive_data": False,
        },
        "consequence_manifest": manifest,
    }


class DecisionPipelineContractTests(unittest.TestCase):
    def test_failed_hard_gate_stops_scoring_even_for_favorable_action(self):
        payload = pipeline()
        payload["hard_gates"]["delegation_valid"] = False
        result = evaluate_pipeline(payload)
        self.assertEqual(result["final_decision"], "DENY")
        self.assertIsNone(result["scoring"])
        self.assertFalse(result["should_execute"])
        self.assertEqual(len(result["stages"]), 1)

    def test_current_authority_can_settle_after_favorable_score(self):
        result = evaluate_pipeline(pipeline(0))
        self.assertEqual(result["scoring"]["posture"], "ALLOW")
        self.assertEqual(result["final_decision"], "SETTLE")
        self.assertTrue(result["should_execute"])
        self.assertTrue(result["should_commit"])

    def test_consequence_time_change_overrides_favorable_score(self):
        result = evaluate_pipeline(pipeline(1))
        self.assertEqual(result["scoring"]["posture"], "ALLOW")
        self.assertEqual(result["final_decision"], "QUARANTINE")
        self.assertTrue(result["should_execute"])
        self.assertFalse(result["should_commit"])
        self.assertIn("hold_commit", result["controls"])

    def test_partial_effect_revocation_requires_compensation(self):
        result = evaluate_pipeline(pipeline(2))
        self.assertEqual(result["final_decision"], "COMPENSATE")
        self.assertIn("execute_compensation", result["controls"])


if __name__ == "__main__":
    unittest.main()

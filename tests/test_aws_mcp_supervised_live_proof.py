import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "examples" / "aws_mcp_supervised_live_proof.json"


class AWSMCPSupervisedLiveProofTests(unittest.TestCase):
    def test_proof_is_read_only_bounded_and_digest_valid(self):
        proof = json.loads(PROOF.read_text(encoding="utf-8"))

        self.assertEqual(proof["schema"], "smerc.aws-mcp-supervised-live-proof.v1")
        self.assertEqual(proof["evidence_class"], "supervised_live_read_only")
        self.assertFalse(proof["production_evidence"])
        self.assertFalse(proof["transport_enforced"])
        self.assertEqual(proof["action"]["tool_name"], "list_regions")
        self.assertEqual(proof["action"]["arguments"], {})
        self.assertFalse(proof["action"]["external_side_effect"])
        self.assertEqual(proof["action"]["estimated_incremental_cost_usd"], 0.0)
        self.assertEqual(proof["smerc_gate"]["posture"], "ALLOW")
        self.assertTrue(proof["smerc_gate"]["should_forward"])
        self.assertFalse(proof["aws_observation"]["resources_created_or_modified"])
        self.assertFalse(proof["aws_observation"]["raw_response_stored"])

        summary = {
            "region_count": proof["aws_observation"]["region_count"],
            "first_region_id": proof["aws_observation"]["first_region_id"],
            "last_region_id": proof["aws_observation"]["last_region_id"],
        }
        encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(encoded).hexdigest(),
            proof["aws_observation"]["sanitized_summary_sha256"],
        )


if __name__ == "__main__":
    unittest.main()

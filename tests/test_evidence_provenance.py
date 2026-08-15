import copy
import hashlib
import json
import unittest
from pathlib import Path

from reference_engine.evidence_program import evaluate_evidence
from reference_engine.evidence_provenance import build_ledger, verify_ledger


ROOT = Path(__file__).resolve().parents[1]
OBSERVATIONS = json.loads(
    (ROOT / "examples" / "evidence_program" / "synthetic_observations.json").read_text(encoding="utf-8")
)
ARTIFACTS = {
    item["observation_id"]: hashlib.sha256(f"artifact:{item['observation_id']}".encode()).hexdigest()
    for item in OBSERVATIONS
}
FIXED_TIME = "2026-07-03T12:00:00Z"


class EvidenceProvenanceTests(unittest.TestCase):
    def build(self, *, key=None):
        return build_ledger(
            OBSERVATIONS,
            program_id="smerc-core-validation-v1",
            collector_id="pilot-collector-1",
            collection_method="controlled-export",
            artifact_digests=ARTIFACTS,
            hmac_key=key,
            recorded_at=FIXED_TIME,
        )

    def test_hash_ledger_is_deterministic_and_verifiable(self):
        ledger = self.build()
        self.assertEqual(ledger, self.build())
        result = verify_ledger(OBSERVATIONS, ledger)
        self.assertEqual(result["status"], "HASH_VERIFIED")
        self.assertEqual(result["record_count"], len(OBSERVATIONS))

    def test_tampered_observation_breaks_admission(self):
        ledger = self.build()
        tampered = copy.deepcopy(OBSERVATIONS)
        tampered[0]["value"] = 0.99
        with self.assertRaisesRegex(ValueError, "does not match"):
            verify_ledger(tampered, ledger)

    def test_broken_chain_or_record_hash_is_rejected(self):
        ledger = self.build()
        ledger["records"][1]["previous_record_hash"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "breaks the ledger chain"):
            verify_ledger(OBSERVATIONS, ledger)

    def test_hmac_ledger_requires_the_correct_secret(self):
        key = b"pilot-secret-key-that-is-at-least-32-bytes"
        ledger = self.build(key=key)
        with self.assertRaisesRegex(ValueError, "HMAC key is required"):
            verify_ledger(OBSERVATIONS, ledger)
        with self.assertRaisesRegex(ValueError, "record_hash is invalid"):
            verify_ledger(OBSERVATIONS, ledger, hmac_key=b"wrong-key-that-is-also-at-least-32-bytes")
        self.assertEqual(verify_ledger(OBSERVATIONS, ledger, hmac_key=key)["status"], "AUTHENTICATED")

    def test_missing_artifact_digest_is_rejected(self):
        incomplete = dict(ARTIFACTS)
        incomplete.pop(OBSERVATIONS[0]["observation_id"])
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            build_ledger(
                OBSERVATIONS,
                program_id="smerc-core-validation-v1",
                collector_id="pilot-collector-1",
                collection_method="controlled-export",
                artifact_digests=incomplete,
                recorded_at=FIXED_TIME,
            )

    def test_hash_only_provenance_caps_otherwise_supported_evidence(self):
        program = {
            "version": "smerc.evidence-program.v1",
            "program_id": "provenance-cap-test",
            "title": "Provenance cap test",
            "claims": [{
                "claim_id": "MOD-001",
                "statement": "A moderate claim is supported.",
                "unknown_class": "operational",
                "risk_level": "moderate",
                "owner_role": "test-owner",
                "failure_consequence": "The test would fail.",
                "criteria": [{
                    "criterion_id": "MOD-001-C1", "metric": "success_rate", "operator": "gte",
                    "threshold": 0.8, "minimum_sample_size": 10,
                    "minimum_source_quality": 0.7, "required_segments": [],
                }],
            }],
        }
        observations = [{
            "observation_id": "obs-1", "claim_id": "MOD-001", "criterion_id": "MOD-001-C1",
            "metric": "success_rate", "value": 0.9, "sample_size": 20, "source_quality": 0.9,
            "segments": [], "source_type": "pilot", "dataset_id": "pilot-1",
            "collected_at": "2026-07-03T12:00:00Z",
        }]
        artifacts = {"obs-1": hashlib.sha256(b"artifact").hexdigest()}
        hash_ledger = build_ledger(
            observations, program_id="provenance-cap-test", collector_id="collector-1",
            collection_method="controlled-export", artifact_digests=artifacts, recorded_at=FIXED_TIME,
        )
        raw = evaluate_evidence(program, observations)
        hash_verified = evaluate_evidence(program, observations, provenance_ledger=hash_ledger)
        key = b"pilot-secret-key-that-is-at-least-32-bytes"
        authenticated_ledger = build_ledger(
            observations, program_id="provenance-cap-test", collector_id="collector-1",
            collection_method="controlled-export", artifact_digests=artifacts,
            hmac_key=key, recorded_at=FIXED_TIME,
        )
        authenticated = evaluate_evidence(
            program, observations, provenance_ledger=authenticated_ledger, provenance_hmac_key=key
        )
        self.assertEqual(raw["deployment_ceiling"], "OBSERVE")
        self.assertEqual(hash_verified["deployment_ceiling"], "RECOMMEND")
        self.assertEqual(authenticated["deployment_ceiling"], "CALIBRATED_ENFORCE")


if __name__ == "__main__":
    unittest.main()

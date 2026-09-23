import copy
import hashlib
import unittest

from reference_engine.deferred_effect_provenance import (
    DeferredEffectError,
    DeferredEffectSigner,
    authorize_deferred_effect,
)


class DeferredEffectProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.signer = DeferredEffectSigner("provenance-key", b"deferred-effect-provenance-test-secret-32")
        self.contract_hash = hashlib.sha256(b"delegated-contract").hexdigest()
        self.intent_hash = hashlib.sha256(b"prepare bounded preview only").hexdigest()
        self.content = b"resource preview_only_configuration {}"
        self.origin = self.signer.attest_origin(
            self.content, artifact_id="artifact-1", artifact_type="terraform",
            tenant_id="smerc-labs", originating_agent_id="preview-agent",
            originating_contract_sha256=self.contract_hash, intent_digest=self.intent_hash,
            authority_ceiling="BOUNDED_WRITE", allowed_effects=["preview", "staging_apply"],
            prohibited_effects=["production_apply"], obligations=["security_review"],
            issued_at=100, expires_at=1000, review_required=True,
        )

    def test_privileged_executor_cannot_launder_low_authority_artifact(self):
        result = authorize_deferred_effect(
            self.signer, self.origin, self.content, effect="production_apply",
            required_authority="PRODUCTION_WRITE", now=200,
        )
        self.assertEqual(result["decision"], "BLOCK")
        self.assertIn("effect_not_in_inherited_authority", result["reasons"])
        self.assertIn("required_authority_exceeds_ceiling", result["reasons"])

    def test_copy_or_transform_keeps_parent_restrictions(self):
        derived = self.signer.derive(
            b"copied and formatted preview configuration", (item for item in [self.origin]),
            artifact_id="artifact-copy", artifact_type="terraform", issued_at=150,
        )
        body = self.signer.verify(derived)
        self.assertEqual(body["authority_ceiling"], "BOUNDED_WRITE")
        self.assertIn("production_apply", body["prohibited_effects"])
        self.assertTrue(body["parent_attestation_sha256"])

    def test_review_must_occur_during_attestation_lifetime(self):
        with self.assertRaisesRegex(DeferredEffectError, "lifetime"):
            self.signer.review(
                self.origin, self.content, reviewer_id="security-owner",
                approved_effects=["staging_apply"], satisfied_obligations=["security_review"],
                reviewed_at=1000,
            )

    def test_combining_artifacts_uses_most_restrictive_effects_and_ceiling(self):
        second = self.signer.attest_origin(
            b"second", artifact_id="artifact-2", artifact_type="workflow",
            tenant_id="smerc-labs", originating_agent_id="read-agent",
            originating_contract_sha256=self.contract_hash, intent_digest=self.intent_hash,
            authority_ceiling="READ", allowed_effects=["preview"], prohibited_effects=["staging_apply"],
            obligations=["owner_review"], issued_at=100, expires_at=800, review_required=False,
        )
        combined = self.signer.derive(
            b"combined", [self.origin, second], artifact_id="combined", artifact_type="bundle", issued_at=200,
        )
        body = self.signer.verify(combined)
        self.assertEqual(body["authority_ceiling"], "READ")
        self.assertEqual(body["allowed_effects"], ["preview"])
        self.assertEqual(body["expires_at"], 800)
        self.assertEqual(body["obligations"], ["owner_review", "security_review"])

    def test_bound_material_review_can_satisfy_obligations(self):
        review = self.signer.review(
            self.origin, self.content, reviewer_id="security-owner",
            approved_effects=["staging_apply"], satisfied_obligations=["security_review"], reviewed_at=200,
        )
        result = authorize_deferred_effect(
            self.signer, self.origin, self.content, effect="staging_apply",
            required_authority="BOUNDED_WRITE", now=250, review=review,
        )
        self.assertEqual(result["decision"], "ALLOW")

    def test_changed_content_and_expired_provenance_are_blocked(self):
        changed = authorize_deferred_effect(
            self.signer, self.origin, b"malicious replacement", effect="staging_apply",
            required_authority="BOUNDED_WRITE", now=200,
        )
        expired = authorize_deferred_effect(
            self.signer, self.origin, self.content, effect="staging_apply",
            required_authority="BOUNDED_WRITE", now=1000,
        )
        self.assertIn("artifact_content_changed", changed["reasons"])
        self.assertIn("provenance_expired", expired["reasons"])

    def test_tampering_is_rejected(self):
        tampered = copy.deepcopy(self.origin)
        tampered["payload"]["authority_ceiling"] = "IRREVERSIBLE"
        with self.assertRaisesRegex(DeferredEffectError, "signature"):
            self.signer.verify(tampered)


if __name__ == "__main__":
    unittest.main()

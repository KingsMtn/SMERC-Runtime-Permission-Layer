import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from reference_engine.policy import DEFAULT_POLICY, PolicyRegistry, RuntimePolicy
from reference_engine.recoverability_engine import RecoverabilityEngine


ROOT = Path(__file__).resolve().parents[1]
POLICY_PAYLOAD = json.loads((ROOT / "examples" / "policies" / "alpha_conservative.json").read_text(encoding="utf-8"))
ACTIONS = json.loads((ROOT / "examples" / "recoverability_action_requests.json").read_text(encoding="utf-8"))
POSTURE_RANK = {"ALLOW": 0, "THROTTLE": 1, "FREEZE": 2, "ESCALATE": 3, "DENY": 4}


class RuntimePolicyTests(unittest.TestCase):
    def test_policy_is_strict_hashed_and_replayable(self):
        policy = RuntimePolicy.from_dict(POLICY_PAYLOAD)
        self.assertEqual(policy.tenant_id, "alpha")
        self.assertEqual(len(policy.policy_hash), 64)
        self.assertEqual(policy.policy_hash, RuntimePolicy.from_dict(policy.to_dict()).policy_hash)
        invalid = copy.deepcopy(POLICY_PAYLOAD)
        invalid["unknown"] = True
        with self.assertRaisesRegex(ValueError, "unknown field"):
            RuntimePolicy.from_dict(invalid)

    def test_policy_mode_cannot_exceed_evidence_ceiling(self):
        invalid = copy.deepcopy(POLICY_PAYLOAD)
        invalid["mode"] = "ENFORCE"
        with self.assertRaisesRegex(ValueError, "exceeds evidence ceiling"):
            RuntimePolicy.from_dict(invalid)

    def test_enforcement_requires_fail_closed_behavior(self):
        invalid = copy.deepcopy(POLICY_PAYLOAD)
        invalid["mode"] = "ENFORCE"
        invalid["evidence_ceiling"] = "LIMITED_ENFORCE"
        with self.assertRaisesRegex(ValueError, "fail_closed"):
            RuntimePolicy.from_dict(invalid)

    def test_incoherent_threshold_order_is_rejected(self):
        invalid = copy.deepcopy(POLICY_PAYLOAD)
        invalid["thresholds"]["deny_exposure_min"] = 0.2
        with self.assertRaisesRegex(ValueError, "deny_exposure_min"):
            RuntimePolicy.from_dict(invalid)

    def test_conservative_policy_is_not_less_restrictive_on_examples(self):
        conservative = RecoverabilityEngine(RuntimePolicy.from_dict(POLICY_PAYLOAD))
        reference = RecoverabilityEngine(DEFAULT_POLICY)
        for action in ACTIONS:
            baseline = reference.evaluate(action)["posture"]
            calibrated = conservative.evaluate(action)["posture"]
            self.assertGreaterEqual(POSTURE_RANK[calibrated], POSTURE_RANK[baseline], action["action_id"])

    def test_decision_and_replay_bind_policy_identity(self):
        policy = RuntimePolicy.from_dict(POLICY_PAYLOAD)
        decision = RecoverabilityEngine(policy).evaluate(ACTIONS[0])
        self.assertEqual(decision["policy"]["policy_hash"], policy.policy_hash)
        self.assertEqual(decision["replay"]["policy"], decision["policy"])

    def test_registry_scopes_policy_by_tenant_and_uses_reference_fallback(self):
        policy = RuntimePolicy.from_dict(POLICY_PAYLOAD)
        registry = PolicyRegistry([policy])
        self.assertEqual(registry.for_tenant("alpha").policy_id, policy.policy_id)
        self.assertEqual(registry.for_tenant("beta").policy_id, DEFAULT_POLICY.policy_id)
        self.assertEqual(registry.count, 1)

    def test_registry_selects_latest_effective_revision_and_never_early_activates(self):
        first = RuntimePolicy.from_dict(POLICY_PAYLOAD)
        later_payload = copy.deepcopy(POLICY_PAYLOAD)
        later_payload["policy_revision"] = "2.0.0"
        later_payload["effective_at"] = "2026-08-01T00:00:00Z"
        later = RuntimePolicy.from_dict(later_payload)
        registry = PolicyRegistry([first, later])
        july = datetime(2026, 7, 15, tzinfo=timezone.utc)
        august = datetime(2026, 8, 2, tzinfo=timezone.utc)
        self.assertEqual(registry.for_tenant("alpha", as_of=july).policy_revision, "1.0.0")
        self.assertEqual(registry.for_tenant("alpha", as_of=august).policy_revision, "2.0.0")

        future_only = PolicyRegistry([later])
        with self.assertRaisesRegex(ValueError, "effective yet"):
            future_only.for_tenant("alpha", as_of=july)


if __name__ == "__main__":
    unittest.main()

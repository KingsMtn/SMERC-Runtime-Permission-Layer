import json
import unittest
from pathlib import Path

from reference_engine.sparta_router import (
    SPARTA_ROUTE_SIGNATURE_VERSION,
    SPARTA_ROUTE_VERSION,
    ToolPlan,
    route_decision,
    sign_route_report,
    verify_signed_route_report,
)


ROOT = Path(__file__).resolve().parents[1]


def load_example(name):
    return json.loads((ROOT / "examples" / "sparta" / name).read_text(encoding="utf-8"))


def plan(**overrides):
    payload = load_example("github_actions_deploy_plan.json")
    payload.update(overrides)
    return payload


def decision(posture="THROTTLE", **overrides):
    payload = {
        "posture": posture,
        "replay_id": f"replay_{posture.lower()}_test_001",
        "reason_codes": ["TEST_REASON"],
        "controls": ["record_replay"],
        "policy": {
            "policy_id": "test-policy",
            "policy_revision": "1.0.0",
            "mode": "ENFORCE",
            "policy_hash": "test-hash",
        },
    }
    payload.update(overrides)
    return payload


class SPARTaRouterTests(unittest.TestCase):
    def test_throttle_routes_to_constrained_execution_when_native_controls_exist(self):
        routed = route_decision(
            decision(
                "THROTTLE",
                controls=["limit_scope", "preview_before_execution", "require_rollback_plan", "record_replay"],
            ),
            plan(requested_scope_units=80, max_scope_units=100),
        )

        self.assertEqual(routed["version"], SPARTA_ROUTE_VERSION)
        self.assertEqual(routed["source_posture"], "THROTTLE")
        self.assertEqual(routed["route_state"], "CONSTRAINED_EXECUTE")
        self.assertTrue(routed["executable"])
        self.assertEqual(routed["effective_scope_units"], 25)
        self.assertIn("limit_scope", routed["applied_controls"])
        self.assertIn("preview_before_execution", routed["applied_controls"])
        self.assertIn("require_rollback_plan", routed["applied_controls"])
        self.assertEqual(routed["blocked_controls"], [])
        self.assertEqual(routed["reason_codes"], ["SPARTA_THROTTLE_WITH_NATIVE_CONTROLS"])

    def test_throttle_requires_review_when_tool_cannot_apply_constraints(self):
        routed = route_decision(
            decision("THROTTLE", controls=["limit_scope", "preview_before_execution", "require_rollback_plan"]),
            plan(
                supports_dry_run=False,
                supports_scope_limit=False,
                supports_checkpoint=False,
                supports_rollback=False,
                side_effect_level="external",
            ),
        )

        self.assertEqual(routed["route_state"], "REVIEW_REQUIRED")
        self.assertFalse(routed["executable"])
        self.assertEqual(routed["effective_scope_units"], 0)
        self.assertIn("scope_limit", routed["blocked_controls"])
        self.assertIn("dry_run", routed["blocked_controls"])
        self.assertIn("checkpoint_or_rollback", routed["blocked_controls"])
        self.assertEqual(routed["reason_codes"], ["SPARTA_CANNOT_CONSTRAIN_TOOL"])

    def test_allow_executes_and_preserves_report(self):
        routed = route_decision(decision("ALLOW"), plan(requested_scope_units=10))

        self.assertEqual(routed["route_state"], "EXECUTE")
        self.assertTrue(routed["executable"])
        self.assertEqual(routed["effective_scope_units"], 10)
        self.assertIn("execute", routed["applied_controls"])
        self.assertIn("record_execution_report", routed["applied_controls"])

    def test_freeze_pauses_without_execution(self):
        routed = route_decision(decision("FREEZE"), plan())

        self.assertEqual(routed["route_state"], "PAUSE")
        self.assertFalse(routed["executable"])
        self.assertEqual(routed["effective_scope_units"], 0)
        self.assertIn("pause_execution", routed["applied_controls"])
        self.assertIn("execute", routed["blocked_controls"])

    def test_deny_blocks_execution(self):
        routed = route_decision(decision("DENY"), plan())

        self.assertEqual(routed["route_state"], "BLOCK")
        self.assertFalse(routed["executable"])
        self.assertIn("block_execution", routed["applied_controls"])
        self.assertIn("execute", routed["blocked_controls"])

    def test_escalate_uses_review_path_when_available(self):
        routed = route_decision(decision("ESCALATE"), plan(supports_human_approval=True))

        self.assertEqual(routed["route_state"], "REVIEW_REQUIRED")
        self.assertFalse(routed["executable"])
        self.assertIn("route_to_accountable_reviewer", routed["applied_controls"])

    def test_escalate_blocks_when_review_path_is_missing(self):
        routed = route_decision(decision("ESCALATE"), plan(supports_human_approval=False))

        self.assertEqual(routed["route_state"], "BLOCKED_ESCALATION_UNAVAILABLE")
        self.assertFalse(routed["executable"])
        self.assertIn("route_to_accountable_reviewer", routed["blocked_controls"])

    def test_invalid_posture_and_unknown_plan_fields_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "decision.posture"):
            route_decision(decision("MAYBE"), plan())

        invalid_plan = plan()
        invalid_plan["shell_command"] = "rm -rf /"
        with self.assertRaisesRegex(ValueError, "unknown field"):
            ToolPlan.from_dict(invalid_plan)

    def test_scope_request_cannot_exceed_declared_maximum(self):
        with self.assertRaisesRegex(ValueError, "requested_scope_units"):
            ToolPlan.from_dict(plan(max_scope_units=10, requested_scope_units=11))

    def test_examples_route_from_disk(self):
        routed = route_decision(load_example("throttle_decision.json"), load_example("github_actions_deploy_plan.json"))

        self.assertEqual(routed["route_state"], "CONSTRAINED_EXECUTE")
        self.assertEqual(routed["decision_replay_id"], "replay_example_throttle_001")
        self.assertEqual(routed["tool_plan"]["tool"], "github_actions")

    def test_signed_route_report_verifies(self):
        routed = route_decision(load_example("throttle_decision.json"), load_example("github_actions_deploy_plan.json"))
        signed = sign_route_report(routed, "test-sparta-route-signing-key", key_id="test-key-1")

        self.assertEqual(signed["signature"]["version"], SPARTA_ROUTE_SIGNATURE_VERSION)
        self.assertEqual(signed["signature"]["algorithm"], "HMAC-SHA256")
        verification = verify_signed_route_report(signed, "test-sparta-route-signing-key")
        self.assertTrue(verification["valid"])
        self.assertEqual(verification["key_id"], "test-key-1")

    def test_signed_route_report_detects_tampering(self):
        routed = route_decision(load_example("throttle_decision.json"), load_example("github_actions_deploy_plan.json"))
        signed = sign_route_report(routed, "test-sparta-route-signing-key")
        signed["route_state"] = "EXECUTE"

        verification = verify_signed_route_report(signed, "test-sparta-route-signing-key")
        self.assertFalse(verification["valid"])
        self.assertIn("route report digest mismatch", verification["errors"])


if __name__ == "__main__":
    unittest.main()

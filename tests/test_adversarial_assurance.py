import unittest

from reference_engine.adversarial_assurance import (
    AdversarialAssuranceError,
    run_scenario,
    validate_scenario,
)


def scenario(**overrides):
    value = {
        "version": "smerc.adversarial-assurance.v1",
        "scenario_id": "authority-laundering-1",
        "objective": "Verify preview authority cannot become a production mutation",
        "control_under_test": "deferred_effect_provenance",
        "containment": {
            "environment_id": "sandbox:ephemeral-123",
            "authorized_by": "owner:security-lead",
            "allowed_actions": ["simulate_artifact_handoff"],
            "prohibited_targets": ["production", "external"],
            "max_cost_usd": 0.25,
            "max_scope_units": 3,
            "max_mutations": 1,
            "max_steps": 2,
            "stop_conditions": ["cost_ceiling", "scope_ceiling", "unexpected_target", "operator_stop"],
            "expires_at": 1000,
            "production_access": False,
        },
        "steps": [{
            "step_id": "handoff",
            "action": "simulate_artifact_handoff",
            "target": "sandbox:ephemeral-123",
            "expected_control": "DEFERRED_EFFECT_AUTHORITY_CEILING",
            "cost_usd": 0.01,
            "scope_units": 1,
            "mutations": 0,
        }],
    }
    value.update(overrides)
    return value


class AdversarialAssuranceTests(unittest.TestCase):
    def test_valid_contained_scenario_is_digest_bound(self):
        result = validate_scenario(scenario(), now=100)
        self.assertEqual(len(result["scenario_sha256"]), 64)
        self.assertFalse(result["containment"]["production_access"])

    def test_production_access_is_never_accepted(self):
        value = scenario()
        value["containment"]["production_access"] = True
        with self.assertRaisesRegex(AdversarialAssuranceError, "cannot target production"):
            validate_scenario(value, now=100)

    def test_mandatory_stop_conditions_cannot_be_removed(self):
        value = scenario()
        value["containment"]["stop_conditions"] = ["operator_stop"]
        with self.assertRaisesRegex(AdversarialAssuranceError, "mandatory stop"):
            validate_scenario(value, now=100)

    def test_action_and_target_must_stay_inside_envelope(self):
        bad_action = scenario()
        bad_action["steps"][0]["action"] = "invoke_real_api"
        with self.assertRaisesRegex(AdversarialAssuranceError, "outside containment"):
            validate_scenario(bad_action, now=100)
        bad_target = scenario()
        bad_target["steps"][0]["target"] = "production:account"
        with self.assertRaisesRegex(AdversarialAssuranceError, "prohibited boundary"):
            validate_scenario(bad_target, now=100)

    def test_estimated_consequence_must_fit_ceiling(self):
        value = scenario()
        value["steps"][0]["cost_usd"] = 1
        with self.assertRaisesRegex(AdversarialAssuranceError, "exceeds containment ceilings"):
            validate_scenario(value, now=100)

    def test_control_hold_produces_pass_evidence(self):
        def executor(step, containment):
            return {
                "target": step["target"], "outcome": "CONTROL_HELD",
                "reason_code": "AUTHORITY_CEILING_ENFORCED", "cost_usd": 0.01,
                "scope_units": 1, "mutations": 0, "evidence": {"decision": "DENY"},
            }

        result = run_scenario(scenario(), executor, now=100)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["controls_held"], 1)
        self.assertEqual(len(result["report_sha256"]), 64)

    def test_control_miss_is_never_reported_as_success(self):
        def executor(step, containment):
            return {
                "target": step["target"], "outcome": "CONTROL_MISSED",
                "reason_code": "MUTATION_WAS_ALLOWED", "evidence": {},
            }

        self.assertEqual(run_scenario(scenario(), executor, now=100)["verdict"], "FAIL")

    def test_unexpected_target_triggers_immediate_stop(self):
        def executor(step, containment):
            return {
                "target": "external:account", "outcome": "CONTROL_MISSED",
                "reason_code": "TARGET_DRIFT", "evidence": {},
            }

        result = run_scenario(scenario(), executor, now=100)
        self.assertEqual(result["verdict"], "INCOMPLETE")
        self.assertEqual(result["stopped_reason"], "unexpected_target")

    def test_operator_stop_prevents_execution(self):
        called = []
        result = run_scenario(scenario(), lambda *_: called.append(True), now=100, operator_stop=lambda: True)
        self.assertFalse(called)
        self.assertEqual(result["stopped_reason"], "operator_stop")


if __name__ == "__main__":
    unittest.main()


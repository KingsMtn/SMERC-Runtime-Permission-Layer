import unittest

from reference_engine.runtime_admission_gate import (
    RUNTIME_ADMISSION_GATE_VERSION,
    evaluate_runtime_admission_gate,
    ref_gate_compat_report,
)


def _payload(**checks):
    values = {
        "identity_valid": True,
        "session_scope_valid": True,
        "permit_valid": True,
        "typed_contract_valid": True,
        "attestation_valid": True,
        "least_privilege_confirmed": True,
        "object_shape_expected": True,
        "required_evidence_present": True,
    }
    values.update(checks)
    return {
        "version": "smerc.runtime-admission-input.v1",
        "request_id": "REQ-001",
        "required_checks": [
            "identity_valid",
            "session_scope_valid",
            "typed_contract_valid",
            "attestation_valid",
            "least_privilege_confirmed",
            "object_shape_expected",
        ],
        "checks": values,
    }


class RuntimeAdmissionGateTests(unittest.TestCase):
    def test_valid_admission_continues_to_recoverability_scoring(self):
        report = evaluate_runtime_admission_gate(_payload())

        self.assertEqual(report["version"], RUNTIME_ADMISSION_GATE_VERSION)
        self.assertEqual(report["decision"], "ADMIT")
        self.assertTrue(report["admissible_for_recoverability_scoring"])
        self.assertEqual(report["max_recommended_posture"], "ALLOW")
        self.assertIn("continue_to_recoverability_scoring", report["required_controls"])

    def test_invalid_identity_rejects_before_scoring(self):
        report = evaluate_runtime_admission_gate(_payload(identity_valid=False))

        self.assertEqual(report["decision"], "REJECT")
        self.assertFalse(report["admissible_for_recoverability_scoring"])
        self.assertEqual(report["max_recommended_posture"], "DENY")
        self.assertIn("identity_invalid", report["drivers"])
        self.assertIn("do_not_use_recoverability_to_rescue_failed_admission", report["required_controls"])

    def test_malformed_tool_shape_rejects_before_scoring(self):
        report = evaluate_runtime_admission_gate(_payload(object_shape_expected=False))

        self.assertEqual(report["decision"], "REJECT")
        self.assertIn("object_shape_unexpected", report["drivers"])
        self.assertIn("OBJECT_SHAPE_UNEXPECTED", report["reason_codes"])

    def test_optional_warning_escalates_without_full_rejection(self):
        report = evaluate_runtime_admission_gate(
            {
                "version": "smerc.runtime-admission-input.v1",
                "request_id": "REQ-OPTIONAL",
                "required_checks": ["identity_valid"],
                "checks": {"identity_valid": True, "permit_valid": False},
            }
        )

        self.assertEqual(report["decision"], "ESCALATE")
        self.assertEqual(report["max_recommended_posture"], "FREEZE")
        self.assertIn("permit_invalid", report["drivers"])

    def test_unknown_required_check_fails_closed(self):
        with self.assertRaises(ValueError):
            evaluate_runtime_admission_gate(
                {
                    "version": "smerc.runtime-admission-input.v1",
                    "request_id": "REQ-BAD",
                    "required_checks": ["made_up_check"],
                    "checks": {},
                }
            )

    def test_ref_gate_compatibility_preserves_existing_shape(self):
        report = ref_gate_compat_report(
            {
                "typed_contract_valid": True,
                "attestation_valid": True,
                "least_privilege_confirmed": True,
                "object_shape_expected": False,
            }
        )

        self.assertEqual(report["pattern"], "deterministic_pre_execution_ref_gate")
        self.assertEqual(report["status"], "fail")
        self.assertIn("object_shape_unexpected", report["drivers"])
        self.assertEqual(report["checks"]["object_shape_expected"]["source"], "explicit")
        self.assertEqual(report["admission_gate"]["decision"], "REJECT")


if __name__ == "__main__":
    unittest.main()

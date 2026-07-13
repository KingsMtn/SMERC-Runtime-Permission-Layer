import copy
import unittest
from pathlib import Path

from reference_engine.control_mapping import (
    CONTROL_LIBRARY_VERSION,
    CONTROL_MAPPING_REPORT_VERSION,
    ControlMappingLibrary,
    render_markdown,
)


EXAMPLE = Path("examples/control_mapping/github_actions_controls.json")


class ControlMappingTests(unittest.TestCase):
    def library(self):
        return ControlMappingLibrary.from_path(EXAMPLE)

    def test_example_library_loads_and_maps_throttle_controls(self):
        library = self.library()
        self.assertEqual(library.to_dict()["version"], CONTROL_LIBRARY_VERSION)
        report = library.map_controls(
            posture="THROTTLE",
            tool="github_actions",
            capability="deploy_production",
            requested_controls=[
                "limit_scope",
                "preview_before_execution",
                "require_rollback_plan",
                "preserve_replay",
            ],
        )
        self.assertEqual(report["version"], CONTROL_MAPPING_REPORT_VERSION)
        self.assertTrue(report["executable"])
        self.assertEqual(report["missing_controls"], [])
        self.assertIn("dry_run_status", report["evidence_requirements"])
        self.assertIn("rollback_ref", report["evidence_requirements"])

    def test_tool_without_native_control_fails_closed(self):
        library = self.library()
        report = library.map_controls(
            posture="ESCALATE",
            tool="github_deployment_adapter",
            capability="deploy_production",
            requested_controls=["route_to_accountable_reviewer", "block_execution"],
        )
        self.assertFalse(report["executable"])
        self.assertEqual(report["missing_controls"][0]["control_id"], "route_to_accountable_reviewer")
        self.assertEqual(report["missing_controls"][0]["failure_behavior"], "fail_closed")
        self.assertEqual(report["mapped_controls"][0]["control_id"], "block_execution")

    def test_unknown_control_is_missing_not_silently_accepted(self):
        library = self.library()
        report = library.map_controls(
            posture="THROTTLE",
            tool="github_actions",
            requested_controls=["limit_scope", "magically_fix_everything"],
        )
        self.assertFalse(report["executable"])
        self.assertEqual(report["missing_controls"][0]["reason"], "control_not_declared")

    def test_controls_not_required_for_posture_do_not_force_execution_failure(self):
        library = self.library()
        report = library.map_controls(
            posture="ALLOW",
            tool="github_actions",
            requested_controls=["limit_scope", "record_replay"],
        )
        self.assertTrue(report["executable"])
        self.assertEqual(report["not_required_controls"][0]["control_id"], "limit_scope")
        self.assertEqual(report["mapped_controls"][0]["control_id"], "record_replay")

    def test_malformed_library_is_rejected_strictly(self):
        payload = self.library().to_dict()
        payload["extra"] = True
        with self.assertRaisesRegex(ValueError, "unknown"):
            ControlMappingLibrary(payload)

        payload = self.library().to_dict()
        payload["controls"][0]["supported_tools"].append("undeclared_tool")
        with self.assertRaisesRegex(ValueError, "unknown tool"):
            ControlMappingLibrary(payload)

        payload = self.library().to_dict()
        payload["controls"][0]["failure_behavior"] = "best_effort"
        with self.assertRaisesRegex(ValueError, "failure_behavior"):
            ControlMappingLibrary(payload)

    def test_duplicate_controls_are_rejected(self):
        payload = self.library().to_dict()
        payload["controls"].append(copy.deepcopy(payload["controls"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate control"):
            ControlMappingLibrary(payload)

    def test_markdown_states_limits(self):
        report = self.library().map_controls(
            posture="THROTTLE",
            tool="github_actions",
            requested_controls=["limit_scope"],
        )
        markdown = render_markdown(report)
        self.assertIn("not proof that a production environment is certified", markdown)
        self.assertIn("limit_scope", markdown)


if __name__ == "__main__":
    unittest.main()

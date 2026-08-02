import copy
import tempfile
import unittest
from pathlib import Path

from reference_engine.operator_status import load_json
from reference_engine.runtime_health_metrics import (
    build_runtime_health_metrics,
    observations_from_decisions,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "reports" / "github_actions_shadow_mode_results.json"
OBSERVATIONS = ROOT / "examples" / "runtime_health_observations.json"
DOC = ROOT / "docs" / "Runtime_Health_Metrics.md"
README = ROOT / "README.md"


class RuntimeHealthMetricsTests(unittest.TestCase):
    def test_builds_latency_volume_and_resilience_metrics(self):
        report = build_runtime_health_metrics(
            decision_artifacts=load_json(DECISIONS),
            observations=load_json(OBSERVATIONS),
            tenant_id="test-tenant",
            latency_slo_ms=250,
        )
        self.assertEqual(report["schema"], "smerc.runtime-health-metrics.v1")
        self.assertEqual(report["health_status"], "healthy")
        self.assertEqual(report["decision_volume"]["decision_count"], 10)
        self.assertEqual(report["decision_volume"]["observed_evaluation_count"], 10)
        self.assertEqual(report["latency"]["p95_ms"], 44.2)
        self.assertTrue(report["latency"]["slo_met"])
        self.assertEqual(report["resilience"]["unavailable_count"], 0)
        self.assertIn("do not prove customer production latency", report["evidence_boundary"])

    def test_missing_observations_keeps_latency_unknown(self):
        report = build_runtime_health_metrics(decision_artifacts=load_json(DECISIONS), observations=None)
        self.assertEqual(report["health_status"], "needs_observations")
        self.assertIsNone(report["latency"]["p95_ms"])
        checks = {check["name"]: check for check in report["operational_checks"]}
        self.assertEqual(checks["observations_present"]["status"], "warning")

    def test_builds_observations_from_api_decision_records(self):
        decisions = {
            "records": [
                {
                    "replay_id": "replay-api-1",
                    "posture": "THROTTLE",
                    "runtime_observation": {
                        "integration_status": "ok",
                        "evaluation_latency_ms": 12.345,
                        "fail_behavior": "not_applicable",
                    },
                },
                {
                    "replay_id": "replay-api-2",
                    "posture": "DENY",
                    "runtime_observation": {
                        "integration_status": "ok",
                        "evaluation_latency_ms": 19.5,
                        "fail_behavior": "not_applicable",
                    },
                },
            ]
        }
        observations = observations_from_decisions(decisions)
        report = build_runtime_health_metrics(
            decision_artifacts=decisions,
            observations=observations,
            latency_slo_ms=250,
        )

        self.assertEqual(observations["schema"], "smerc.runtime-health-observations.v1")
        self.assertEqual(observations["evidence_status"], "api_observed_runtime")
        self.assertEqual(report["decision_volume"]["observed_evaluation_count"], 2)
        self.assertEqual(report["latency"]["sample_count"], 2)
        self.assertIsNotNone(report["latency"]["p95_ms"])

    def test_unavailable_and_latency_thresholds_degrade_or_block(self):
        observations = load_json(OBSERVATIONS)
        slow = copy.deepcopy(observations)
        slow["records"][0]["evaluation_latency_ms"] = 900
        degraded = build_runtime_health_metrics(
            decision_artifacts=load_json(DECISIONS),
            observations=slow,
            latency_slo_ms=100,
        )
        self.assertEqual(degraded["health_status"], "degraded")
        self.assertFalse(degraded["latency"]["slo_met"])

        unavailable = copy.deepcopy(observations)
        unavailable["records"][0]["integration_status"] = "unavailable"
        blocked = build_runtime_health_metrics(
            decision_artifacts=load_json(DECISIONS),
            observations=unavailable,
            unavailable_rate_blocker=0.05,
        )
        self.assertEqual(blocked["health_status"], "blocked")
        self.assertEqual(blocked["resilience"]["unavailable_count"], 1)

    def test_writes_outputs_and_docs_are_linked(self):
        report = build_runtime_health_metrics(
            decision_artifacts=load_json(DECISIONS),
            observations=load_json(OBSERVATIONS),
        )
        markdown = render_markdown(report)
        self.assertIn("SMERC Runtime Health Metrics", markdown)
        self.assertIn("Evidence Boundary", markdown)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "health.json"
            markdown_path = Path(directory) / "health.md"
            write_outputs(report, json_path=json_path, markdown_path=markdown_path)
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())

        doc = DOC.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        self.assertIn("python -m reference_engine.runtime_health_metrics --pretty", doc)
        self.assertIn("docs/Runtime_Health_Metrics.md", readme)


if __name__ == "__main__":
    unittest.main()

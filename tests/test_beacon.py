import json
import unittest
from pathlib import Path

from reference_engine.beacon import validate_beacon


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "smerc_beacon.json"


class BeaconTests(unittest.TestCase):
    def setUp(self):
        self.beacon = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_example_beacon_is_valid(self):
        result = validate_beacon(self.beacon)
        self.assertTrue(result["valid"])
        self.assertEqual(result["schema_version"], "smerc.beacon.v1")
        self.assertEqual(result["posture_count"], 5)

    def test_requires_discovery_endpoints(self):
        broken = dict(self.beacon)
        broken["discovery_endpoints"] = {"llms": self.beacon["discovery_endpoints"]["llms"]}
        with self.assertRaises(ValueError):
            validate_beacon(broken)

    def test_rejects_non_https_public_links(self):
        broken = dict(self.beacon)
        broken["canonical_site"] = "http://example.test"
        with self.assertRaises(ValueError):
            validate_beacon(broken)

    def test_rejects_overclaim_language(self):
        broken = dict(self.beacon)
        broken["status"] = "production-certified"
        with self.assertRaises(ValueError):
            validate_beacon(broken)

    def test_model_agent_fitness_signals_are_present(self):
        fitness = self.beacon["model_agent_fitness"]
        self.assertIn("data_sensitivity", fitness["input_signals"])
        self.assertIn("recommended_executor", fitness["output_fields"])


if __name__ == "__main__":
    unittest.main()

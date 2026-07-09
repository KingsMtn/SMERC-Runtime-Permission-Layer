import json
import unittest
from pathlib import Path

from reference_engine.sparta_registry import (
    SPARTA_ADAPTER_REGISTRY_VERSION,
    SPARTaAdapterRegistry,
    load_sparta_adapter_registry,
)


ROOT = Path(__file__).resolve().parents[1]


class SPARTaAdapterRegistryTests(unittest.TestCase):
    def test_example_registry_builds_tool_plan(self):
        registry = load_sparta_adapter_registry(ROOT / "examples" / "sparta" / "adapter_registry.json")
        plan = registry.plan_from_request(
            {
                "adapter_id": "github-actions-deployer",
                "action": "deploy_canary",
                "requested_capability": "deployment",
                "requested_scope_units": 40,
                "side_effect_level": "external",
                "metadata": {"workflow_run": "1001"},
            }
        )

        self.assertEqual(registry.count, 2)
        self.assertEqual(plan.tool, "github_actions")
        self.assertEqual(plan.action, "deploy_canary")
        self.assertEqual(plan.requested_scope_units, 40)
        self.assertTrue(plan.supports_rollback)
        self.assertEqual(plan.metadata["workflow_run"], "1001")

    def test_registry_rejects_duplicate_unknown_and_excessive_requests(self):
        source = json.loads((ROOT / "examples" / "sparta" / "adapter_registry.json").read_text(encoding="utf-8"))
        source["adapters"].append(dict(source["adapters"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            SPARTaAdapterRegistry.from_dict(source)

        registry = load_sparta_adapter_registry(ROOT / "examples" / "sparta" / "adapter_registry.json")
        with self.assertRaisesRegex(ValueError, "does not support action"):
            registry.plan_from_request(
                {
                    "adapter_id": "github-actions-deployer",
                    "action": "delete_database",
                    "requested_capability": "deployment",
                    "requested_scope_units": 1,
                    "side_effect_level": "external",
                    "metadata": {},
                }
            )
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            registry.plan_from_request(
                {
                    "adapter_id": "github-actions-deployer",
                    "action": "deploy_canary",
                    "requested_capability": "deployment",
                    "requested_scope_units": 101,
                    "side_effect_level": "external",
                    "metadata": {},
                }
            )

    def test_registry_shape_is_strict(self):
        with self.assertRaisesRegex(ValueError, "registry.version"):
            SPARTaAdapterRegistry.from_dict({"version": "wrong", "adapters": []})
        with self.assertRaisesRegex(ValueError, "unknown field"):
            SPARTaAdapterRegistry.from_dict(
                {"version": SPARTA_ADAPTER_REGISTRY_VERSION, "adapters": [], "surprise": True}
            )


if __name__ == "__main__":
    unittest.main()

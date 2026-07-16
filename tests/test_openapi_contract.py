import json
import unittest
from pathlib import Path

from api_server import schema


ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "schemas" / "smerc-runtime-api-openapi-v1.json"


class OpenAPIContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(OPENAPI.read_text(encoding="utf-8"))

    def test_contract_is_valid_json_openapi_31(self):
        self.assertEqual(self.contract["openapi"], "3.1.0")
        self.assertEqual(self.contract["info"]["version"], "smerc.runtime-api.v1")
        self.assertIn("bearerAuth", self.contract["components"]["securitySchemes"])

    def test_contract_includes_runtime_schema_endpoints(self):
        documented = {
            f"{method.upper()} {path}"
            for path, operations in self.contract["paths"].items()
            for method in operations
        }
        runtime_endpoints = set(schema()["endpoints"])
        missing = sorted(
            endpoint for endpoint in runtime_endpoints
            if _normalize_endpoint(endpoint) not in documented
        )
        self.assertEqual(missing, [])

    def test_agent_handshake_contract_declares_scope_and_replay_fields(self):
        operation = self.contract["paths"]["/v1/agent/handshake"]["post"]
        self.assertIn("actions.evaluate", operation["description"])
        response_schema = self.contract["components"]["schemas"]["AgentHandshakeResponse"]
        self.assertIn("handshake_posture", response_schema["required"])
        self.assertIn("fitness_replay_id", response_schema["properties"]["replay"]["required"])
        self.assertIn("action_replay_id", response_schema["properties"]["replay"]["required"])

    def test_contract_keeps_pilot_boundary_language(self):
        description = self.contract["info"]["description"]
        self.assertIn("pilot", description.lower())
        self.assertIn("not a production certification", description.lower())


def _normalize_endpoint(endpoint: str) -> str:
    method, path = endpoint.split(" ", 1)
    if path in {"/health", "/ready", "/schema"}:
        path = f"/v1{path}"
    return f"{method} {path}"


if __name__ == "__main__":
    unittest.main()

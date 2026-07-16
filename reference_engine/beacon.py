from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


REQUIRED_TOP_LEVEL = [
    "schema_version",
    "name",
    "category",
    "canonical_site",
    "canonical_repository",
    "one_line_summary",
    "status",
    "postures",
    "core_questions",
    "governance_surfaces",
    "discovery_endpoints",
    "model_agent_fitness",
    "non_claims",
    "review_paths",
]

REQUIRED_POSTURES = {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"}

DISALLOWED_CLAIMS = [
    "production-certified",
    "guaranteed",
    "eliminates incidents",
    "prevents all",
    "replaces iam",
    "replaces opa",
    "replaces ai gateways",
]


def validate_beacon(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a public SMERC beacon manifest without third-party dependencies."""
    if not isinstance(payload, dict):
        raise TypeError("beacon payload must be an object")

    missing = [key for key in REQUIRED_TOP_LEVEL if key not in payload]
    if missing:
        raise ValueError(f"Missing required beacon field(s): {', '.join(missing)}")

    if payload["schema_version"] != "smerc.beacon.v1":
        raise ValueError("schema_version must be smerc.beacon.v1")

    for key in ["name", "category", "canonical_site", "canonical_repository", "one_line_summary", "status"]:
        _require_non_empty_string(payload[key], key)

    if not payload["canonical_site"].startswith("https://"):
        raise ValueError("canonical_site must be an https URL")
    if not payload["canonical_repository"].startswith("https://github.com/"):
        raise ValueError("canonical_repository must be a GitHub URL")

    postures = payload["postures"]
    if not isinstance(postures, list) or set(postures) != REQUIRED_POSTURES:
        raise ValueError("postures must contain ALLOW, THROTTLE, FREEZE, DENY, and ESCALATE")

    for key in ["core_questions", "governance_surfaces", "non_claims"]:
        _require_string_list(payload[key], key, min_items=3)

    discovery = payload["discovery_endpoints"]
    if not isinstance(discovery, dict):
        raise TypeError("discovery_endpoints must be an object")
    for key in ["llms", "humans", "project_profile", "beacon", "sitemap"]:
        if key not in discovery:
            raise ValueError(f"discovery_endpoints missing {key}")
        _require_https_url(discovery[key], f"discovery_endpoints.{key}")

    fitness = payload["model_agent_fitness"]
    if not isinstance(fitness, dict):
        raise TypeError("model_agent_fitness must be an object")
    for key in ["purpose", "input_signals", "output_fields"]:
        if key not in fitness:
            raise ValueError(f"model_agent_fitness missing {key}")
    _require_non_empty_string(fitness["purpose"], "model_agent_fitness.purpose")
    _require_string_list(fitness["input_signals"], "model_agent_fitness.input_signals", min_items=5)
    _require_string_list(fitness["output_fields"], "model_agent_fitness.output_fields", min_items=5)

    review_paths = payload["review_paths"]
    if not isinstance(review_paths, dict) or not review_paths:
        raise TypeError("review_paths must be a non-empty object")
    for key, value in review_paths.items():
        _require_https_url(value, f"review_paths.{key}")

    text = json.dumps(payload, sort_keys=True).lower()
    overclaims = [claim for claim in DISALLOWED_CLAIMS if claim in text]
    if overclaims:
        raise ValueError(f"beacon contains disallowed overclaim(s): {', '.join(overclaims)}")

    return {
        "schema_version": payload["schema_version"],
        "name": payload["name"],
        "valid": True,
        "posture_count": len(postures),
        "surface_count": len(payload["governance_surfaces"]),
        "discovery_endpoint_count": len(discovery),
        "review_path_count": len(review_paths),
    }


def load_beacon(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_non_empty_string(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{field_name} must be a non-empty string")


def _require_string_list(value: Any, field_name: str, min_items: int) -> None:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list")
    if len(value) < min_items:
        raise ValueError(f"{field_name} must contain at least {min_items} items")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise TypeError(f"{field_name} must contain only non-empty strings")


def _require_https_url(value: Any, field_name: str) -> None:
    _require_non_empty_string(value, field_name)
    if not value.startswith("https://"):
        raise ValueError(f"{field_name} must be an https URL")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a SMERC beacon manifest.")
    parser.add_argument("input", type=Path, help="Path to a smerc.beacon.v1 JSON manifest")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print validation output")
    args = parser.parse_args()

    result = validate_beacon(load_beacon(args.input))
    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

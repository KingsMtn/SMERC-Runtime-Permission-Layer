from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.design_partner_fit import assess as assess_fit


VERSION = "smerc.first-pilot-packet.v1"
MANIFEST_VERSION = "smerc.github_actions_pilot_manifest.v1"


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def validate_manifest(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {
        "schema",
        "pilot_name",
        "pilot_status",
        "pilot_boundary",
        "target_workflows",
        "authentication_options",
        "customer_roles",
        "smerc_roles",
        "weekly_metrics",
        "stop_conditions",
        "go_no_go_options",
        "required_repository_evidence",
    }
    unknown = sorted(set(payload) - required)
    missing = sorted(required - set(payload))
    if unknown:
        raise ValueError(f"pilot manifest contains unknown field(s): {', '.join(unknown)}")
    if missing:
        raise ValueError(f"pilot manifest is missing field(s): {', '.join(missing)}")
    if payload["schema"] != MANIFEST_VERSION:
        raise ValueError(f"pilot manifest schema must be {MANIFEST_VERSION}")

    boundary = payload["pilot_boundary"]
    auth = payload["authentication_options"]
    workflows = payload["target_workflows"]
    if not isinstance(boundary, dict):
        raise TypeError("pilot_boundary must be an object")
    if boundary.get("mode") != "observe":
        raise ValueError("first pilot manifest must start in observe mode")
    if boundary.get("not_production_certified") is not True:
        raise ValueError("first pilot manifest must explicitly mark not_production_certified true")
    if not _string_list(boundary.get("approved_data")):
        raise ValueError("approved_data must be a non-empty string list")
    if not _string_list(boundary.get("excluded_data")):
        raise ValueError("excluded_data must be a non-empty string list")
    if not isinstance(auth, dict) or auth.get("preferred") not in {"github-oidc", "scoped-static-credential"}:
        raise ValueError("authentication_options.preferred must be github-oidc or scoped-static-credential")
    if not isinstance(workflows, list) or not workflows:
        raise ValueError("target_workflows must be a non-empty list")

    return {
        "pilot_name": _text(payload["pilot_name"], "pilot_name"),
        "pilot_status": _text(payload["pilot_status"], "pilot_status"),
        "pilot_boundary": {
            "mode": boundary["mode"],
            "not_production_certified": True,
            "approved_data": _string_list(boundary["approved_data"]),
            "excluded_data": _string_list(boundary["excluded_data"]),
        },
        "target_workflows": [_workflow(item, index) for index, item in enumerate(workflows)],
        "authentication_options": {
            "preferred": auth["preferred"],
            "accepted": _string_list(auth.get("accepted", [])),
            "static_credential_secret_name": _text(
                auth.get("static_credential_secret_name", "SMERC_API_KEY"),
                "authentication_options.static_credential_secret_name",
            ),
            "api_url_variable_name": _text(
                auth.get("api_url_variable_name", "SMERC_API_URL"),
                "authentication_options.api_url_variable_name",
            ),
        },
        "customer_roles": _string_list(payload["customer_roles"]),
        "smerc_roles": _string_list(payload["smerc_roles"]),
        "weekly_metrics": _string_list(payload["weekly_metrics"]),
        "stop_conditions": _string_list(payload["stop_conditions"]),
        "go_no_go_options": _string_list(payload["go_no_go_options"]),
        "required_repository_evidence": _string_list(payload["required_repository_evidence"]),
    }


def _workflow(value: Any, index: int) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"target_workflows[{index}] must be an object")
    required = {"workflow_name", "repository_scope", "trigger_scope", "initial_mode", "evidence_artifact"}
    missing = sorted(required - set(value))
    unknown = sorted(set(value) - required)
    if missing or unknown:
        raise ValueError(f"target_workflows[{index}] must contain only required workflow fields")
    if value["initial_mode"] != "observe":
        raise ValueError(f"target_workflows[{index}].initial_mode must be observe")
    return {
        "workflow_name": _text(value["workflow_name"], f"target_workflows[{index}].workflow_name"),
        "repository_scope": _text(value["repository_scope"], f"target_workflows[{index}].repository_scope"),
        "trigger_scope": _string_list(value["trigger_scope"]),
        "initial_mode": "observe",
        "evidence_artifact": _text(value["evidence_artifact"], f"target_workflows[{index}].evidence_artifact"),
    }


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise TypeError("expected a non-empty list")
    parsed = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise TypeError("list items must be non-empty strings")
        parsed.append(item.strip())
    return parsed


def build_packet(manifest_payload: Mapping[str, Any], fit_payload: Mapping[str, Any]) -> Dict[str, Any]:
    manifest = validate_manifest(manifest_payload)
    fit = assess_fit(fit_payload)
    blockers = list(fit["blockers"])
    ready_to_start = fit["fit"] in {"moderate", "strong"} and not blockers
    if manifest["pilot_boundary"]["mode"] != "observe":
        blockers.append("First pilot is not in observe mode.")
        ready_to_start = False
    return {
        "schema": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pilot_name": manifest["pilot_name"],
        "pilot_status": manifest["pilot_status"],
        "ready_to_start": ready_to_start,
        "recommended_offer": fit["recommendation"],
        "fit": {
            "organization": fit["organization"],
            "assessment_date": fit["assessment_date"],
            "total_score": fit["total_score"],
            "maximum_score": fit["maximum_score"],
            "fit_band": fit["fit"],
            "blockers": blockers,
        },
        "pilot_boundary": manifest["pilot_boundary"],
        "target_workflows": manifest["target_workflows"],
        "authentication": manifest["authentication_options"],
        "roles": {
            "customer": manifest["customer_roles"],
            "smerc": manifest["smerc_roles"],
        },
        "weekly_metrics": manifest["weekly_metrics"],
        "stop_conditions": manifest["stop_conditions"],
        "go_no_go_options": manifest["go_no_go_options"],
        "required_repository_evidence": manifest["required_repository_evidence"],
        "first_30_days": [
            "Week zero: confirm fit, data boundary, owner, reviewer capacity, and success metrics.",
            "Week one: install observe-mode scoring and inspect first decision artifacts.",
            "Weeks two through four: compare posture decisions with reviewer judgment.",
            "Day 30: decide stop, narrow, continue observe, or move to recommend.",
        ],
        "evidence_boundary": "Pilot packet only. It does not prove production readiness, customer demand, incident reduction, or compliance.",
    }


def markdown(packet: Mapping[str, Any]) -> str:
    lines = [
        f"# {packet['pilot_name']} First Pilot Packet",
        "",
        f"Generated: `{packet['generated_at']}`",
        "",
        "## Start Decision",
        "",
        f"- Ready to start: `{str(packet['ready_to_start']).lower()}`",
        f"- Fit band: `{packet['fit']['fit_band']}`",
        f"- Fit score: `{packet['fit']['total_score']}` of `{packet['fit']['maximum_score']}`",
        f"- Recommended offer: {packet['recommended_offer']}",
        "",
        "## Blockers",
        "",
    ]
    if packet["fit"]["blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["fit"]["blockers"])
    else:
        lines.append("- None identified by this screen.")
    lines.extend(
        [
            "",
            "## Pilot Boundary",
            "",
            f"- Mode: `{packet['pilot_boundary']['mode']}`",
            f"- Not production-certified: `{str(packet['pilot_boundary']['not_production_certified']).lower()}`",
            "",
            "Approved data:",
        ]
    )
    lines.extend(f"- {item}" for item in packet["pilot_boundary"]["approved_data"])
    lines.append("")
    lines.append("Excluded data:")
    lines.extend(f"- {item}" for item in packet["pilot_boundary"]["excluded_data"])
    lines.extend(["", "## Target Workflows", "", "| Workflow | Repository Scope | Triggers | Artifact |", "| --- | --- | --- | --- |"])
    for workflow in packet["target_workflows"]:
        lines.append(
            f"| {safe(workflow['workflow_name'])} | {safe(workflow['repository_scope'])} | {safe(', '.join(workflow['trigger_scope']))} | `{safe(workflow['evidence_artifact'])}` |"
        )
    lines.extend(["", "## First 30 Days", ""])
    lines.extend(f"- {item}" for item in packet["first_30_days"])
    lines.extend(["", "## Weekly Metrics", ""])
    lines.extend(f"- {item}" for item in packet["weekly_metrics"])
    lines.extend(["", "## Stop Conditions", ""])
    lines.extend(f"- {item}" for item in packet["stop_conditions"])
    lines.extend(["", "## Go/No-Go Options", ""])
    lines.extend(f"- {item}" for item in packet["go_no_go_options"])
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            str(packet["evidence_boundary"]),
        ]
    )
    return "\n".join(lines) + "\n"


def safe(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a SMERC first-pilot packet.")
    parser.add_argument("--manifest", type=Path, default=Path("examples/github_actions_pilot_manifest.json"))
    parser.add_argument("--fit", type=Path, default=Path("examples/design_partner_fit_example.json"))
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    packet = build_packet(load_json(args.manifest), load_json(args.fit))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown(packet), encoding="utf-8")
    print(json.dumps(packet, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


CONTROL_LIBRARY_VERSION = "smerc.control-mapping-library.v1"
CONTROL_MAPPING_REPORT_VERSION = "smerc.control-mapping-report.v1"
POSTURES = {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"}
CONTROL_OUTCOMES = {"mapped", "missing", "not_required_for_posture"}
FAILURE_BEHAVIORS = {"fail_closed", "route_to_review", "block_execution", "record_only"}

LIBRARY_FIELDS = {"version", "library_id", "description", "tools", "controls"}
TOOL_FIELDS = {"tool", "native_capabilities", "notes"}
CONTROL_FIELDS = {
    "control_id",
    "description",
    "required_for_postures",
    "supported_tools",
    "native_mechanism",
    "evidence_required",
    "failure_behavior",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _strict_object(value: Any, fields: set[str], path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    missing = sorted(fields - set(value))
    if missing:
        raise ValueError(f"{path} is missing required field(s): {', '.join(missing)}")
    unknown = sorted(set(value) - fields)
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")
    return dict(value)


def _identifier(value: Any, path: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,%d}" % (maximum - 1), value):
        raise ValueError(f"{path} must be a safe identifier of 1 to {maximum} characters")
    return value


def _text(value: Any, path: str, maximum: int = 512) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _list_of_identifiers(value: Any, path: str, maximum_items: int = 64) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"{path} must be a list")
    if len(value) > maximum_items:
        raise ValueError(f"{path} must contain at most {maximum_items} items")
    return [_identifier(item, f"{path}[]") for item in value]


def _postures(value: Any, path: str) -> list[str]:
    postures = _list_of_identifiers(value, path, len(POSTURES))
    unknown = sorted(set(postures) - POSTURES)
    if unknown:
        raise ValueError(f"{path} contains unsupported posture(s): {', '.join(unknown)}")
    return sorted(set(postures))


def _mechanisms(value: Any, path: str) -> Dict[str, str]:
    if not isinstance(value, dict) or not value:
        raise TypeError(f"{path} must be a non-empty object")
    parsed: Dict[str, str] = {}
    for tool, mechanism in value.items():
        parsed[_identifier(tool, f"{path}.tool")] = _text(mechanism, f"{path}.{tool}", 256)
    return dict(sorted(parsed.items()))


def _validate_library(payload: Mapping[str, Any]) -> Dict[str, Any]:
    library = _strict_object(dict(payload), LIBRARY_FIELDS, "control_library")
    if library["version"] != CONTROL_LIBRARY_VERSION:
        raise ValueError(f"control_library.version must be {CONTROL_LIBRARY_VERSION}")
    library_id = _identifier(library["library_id"], "control_library.library_id")
    description = _text(library["description"], "control_library.description", 512)

    tools_value = library["tools"]
    if not isinstance(tools_value, list) or not tools_value:
        raise TypeError("control_library.tools must be a non-empty list")
    tools: Dict[str, Dict[str, Any]] = {}
    for index, item in enumerate(tools_value):
        tool = _strict_object(item, TOOL_FIELDS, f"control_library.tools[{index}]")
        tool_id = _identifier(tool["tool"], f"control_library.tools[{index}].tool")
        if tool_id in tools:
            raise ValueError(f"duplicate tool declared: {tool_id}")
        tools[tool_id] = {
            "tool": tool_id,
            "native_capabilities": _list_of_identifiers(
                tool["native_capabilities"],
                f"control_library.tools[{index}].native_capabilities",
            ),
            "notes": _text(tool["notes"], f"control_library.tools[{index}].notes", 512),
        }

    controls_value = library["controls"]
    if not isinstance(controls_value, list) or not controls_value:
        raise TypeError("control_library.controls must be a non-empty list")
    controls: Dict[str, Dict[str, Any]] = {}
    for index, item in enumerate(controls_value):
        control = _strict_object(item, CONTROL_FIELDS, f"control_library.controls[{index}]")
        control_id = _identifier(control["control_id"], f"control_library.controls[{index}].control_id")
        if control_id in controls:
            raise ValueError(f"duplicate control declared: {control_id}")
        supported_tools = _list_of_identifiers(
            control["supported_tools"],
            f"control_library.controls[{index}].supported_tools",
        )
        unknown_tools = sorted(set(supported_tools) - set(tools))
        if unknown_tools:
            raise ValueError(f"control {control_id} references unknown tool(s): {', '.join(unknown_tools)}")
        mechanisms = _mechanisms(control["native_mechanism"], f"control_library.controls[{index}].native_mechanism")
        missing_mechanisms = sorted(set(supported_tools) - set(mechanisms))
        if missing_mechanisms:
            raise ValueError(f"control {control_id} is missing native mechanism(s): {', '.join(missing_mechanisms)}")
        failure_behavior = _identifier(
            control["failure_behavior"],
            f"control_library.controls[{index}].failure_behavior",
        )
        if failure_behavior not in FAILURE_BEHAVIORS:
            raise ValueError(f"control {control_id} has unsupported failure_behavior")
        controls[control_id] = {
            "control_id": control_id,
            "description": _text(control["description"], f"control_library.controls[{index}].description", 512),
            "required_for_postures": _postures(
                control["required_for_postures"],
                f"control_library.controls[{index}].required_for_postures",
            ),
            "supported_tools": sorted(set(supported_tools)),
            "native_mechanism": mechanisms,
            "evidence_required": _list_of_identifiers(
                control["evidence_required"],
                f"control_library.controls[{index}].evidence_required",
            ),
            "failure_behavior": failure_behavior,
        }

    return {
        "version": CONTROL_LIBRARY_VERSION,
        "library_id": library_id,
        "description": description,
        "tools": [tools[key] for key in sorted(tools)],
        "controls": [controls[key] for key in sorted(controls)],
    }


class ControlMappingLibrary:
    """Maps abstract SMERC controls to native mechanisms declared by a tool."""

    def __init__(self, payload: Mapping[str, Any]) -> None:
        self.data = _validate_library(payload)
        self.controls = {item["control_id"]: item for item in self.data["controls"]}
        self.tools = {item["tool"]: item for item in self.data["tools"]}

    @classmethod
    def from_path(cls, path: str | Path) -> "ControlMappingLibrary":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls(json.load(handle))

    def to_dict(self) -> Dict[str, Any]:
        return json.loads(_canonical_json(self.data))

    def map_controls(
        self,
        *,
        posture: str,
        tool: str,
        requested_controls: Iterable[str],
        capability: str = "unspecified",
    ) -> Dict[str, Any]:
        if posture not in POSTURES:
            raise ValueError(f"posture must be one of {', '.join(sorted(POSTURES))}")
        tool = _identifier(tool, "tool")
        if tool not in self.tools:
            raise ValueError(f"tool is not declared in this control library: {tool}")
        capability = _identifier(capability, "capability")
        requested = sorted({_identifier(item, "requested_controls[]") for item in requested_controls})
        mapped = []
        missing = []
        not_required = []
        evidence_requirements = set()

        for control_id in requested:
            control = self.controls.get(control_id)
            if control is None:
                missing.append(
                    {
                        "control_id": control_id,
                        "outcome": "missing",
                        "reason": "control_not_declared",
                        "failure_behavior": "fail_closed",
                    }
                )
                continue
            if posture not in control["required_for_postures"]:
                not_required.append(
                    {
                        "control_id": control_id,
                        "outcome": "not_required_for_posture",
                        "reason": f"{control_id} is not required for {posture}",
                    }
                )
                continue
            if tool not in control["supported_tools"]:
                missing.append(
                    {
                        "control_id": control_id,
                        "outcome": "missing",
                        "reason": "tool_does_not_support_control",
                        "failure_behavior": control["failure_behavior"],
                    }
                )
                continue
            mapped.append(
                {
                    "control_id": control_id,
                    "outcome": "mapped",
                    "native_mechanism": control["native_mechanism"][tool],
                    "evidence_required": control["evidence_required"],
                    "failure_behavior": control["failure_behavior"],
                }
            )
            evidence_requirements.update(control["evidence_required"])

        executable = len(missing) == 0
        recommended_next_action = (
            "Proceed only through an adapter that applies the mapped native controls and records evidence."
            if executable
            else "Do not execute automatically. Route to review or replace the tool path with one that supports the missing controls."
        )
        return {
            "version": CONTROL_MAPPING_REPORT_VERSION,
            "library_id": self.data["library_id"],
            "posture": posture,
            "tool": tool,
            "capability": capability,
            "requested_controls": requested,
            "mapped_controls": sorted(mapped, key=lambda item: item["control_id"]),
            "missing_controls": sorted(missing, key=lambda item: item["control_id"]),
            "not_required_controls": sorted(not_required, key=lambda item: item["control_id"]),
            "evidence_requirements": sorted(evidence_requirements),
            "executable": executable,
            "recommended_next_action": recommended_next_action,
            "plain_english_summary": _summary(posture, tool, mapped, missing),
        }


def _summary(posture: str, tool: str, mapped: list[Mapping[str, Any]], missing: list[Mapping[str, Any]]) -> str:
    if missing:
        return (
            f"SMERC posture {posture} cannot be executed through {tool} until "
            f"{len(missing)} required control(s) are supported or reviewed."
        )
    return (
        f"SMERC posture {posture} maps to {len(mapped)} native control(s) for {tool}; "
        "execution should remain evidence-bound."
    )


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Control Mapping Report",
        "",
        "This report maps abstract SMERC controls to declared native mechanisms for one tool path.",
        "It is pilot evidence, not proof that a production environment is certified or continuously enforced.",
        "",
        f"- Library: `{report['library_id']}`",
        f"- Posture: `{report['posture']}`",
        f"- Tool: `{report['tool']}`",
        f"- Capability: `{report['capability']}`",
        f"- Executable: `{str(report['executable']).lower()}`",
        "",
        "## Mapped Controls",
        "",
    ]
    if report["mapped_controls"]:
        lines.append("| Control | Native mechanism | Evidence required |")
        lines.append("| --- | --- | --- |")
        for control in report["mapped_controls"]:
            evidence = ", ".join(f"`{item}`" for item in control["evidence_required"])
            lines.append(
                f"| `{control['control_id']}` | {control['native_mechanism']} | {evidence} |"
            )
    else:
        lines.append("No requested controls mapped to native mechanisms.")
    lines.extend(["", "## Missing Controls", ""])
    if report["missing_controls"]:
        lines.append("| Control | Reason | Failure behavior |")
        lines.append("| --- | --- | --- |")
        for control in report["missing_controls"]:
            lines.append(
                f"| `{control['control_id']}` | {control['reason']} | `{control['failure_behavior']}` |"
            )
    else:
        lines.append("No required controls are missing for this mapping.")
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            report["recommended_next_action"],
            "",
            report["plain_english_summary"],
            "",
        ]
    )
    return "\n".join(lines)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Map SMERC controls to native tool mechanisms.")
    parser.add_argument("library", help="Path to a SMERC control mapping library JSON file.")
    parser.add_argument("--posture", required=True, choices=sorted(POSTURES))
    parser.add_argument("--tool", required=True)
    parser.add_argument("--capability", default="unspecified")
    parser.add_argument("--controls", nargs="+", required=True)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--json-output")
    parser.add_argument("--markdown-output")
    args = parser.parse_args()

    library = ControlMappingLibrary.from_path(args.library)
    report = library.map_controls(
        posture=args.posture,
        tool=args.tool,
        capability=args.capability,
        requested_controls=args.controls,
    )
    if args.json_output:
        _write_json(Path(args.json_output), report)
    if args.markdown_output:
        _write_text(Path(args.markdown_output), render_markdown(report))
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

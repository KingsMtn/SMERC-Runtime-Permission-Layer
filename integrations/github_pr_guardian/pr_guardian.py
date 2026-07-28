from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


PR_GUARDIAN_CERTIFICATE_VERSION = "smerc.github-pr-guardian-certificate.v1"
PR_COMMENT_MARKER = "<!-- smerc-pr-guardian:v1 -->"
VALID_POSTURES = {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE", "UNAVAILABLE"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: Mapping[str, Any]) -> str:
    material = {key: item for key, item in value.items() if key not in {"certificate_digest", "verification"}}
    return hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()


def _load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def _score(decision: Mapping[str, Any] | None, field: str) -> Any:
    if decision is None:
        return None
    if field == "risk":
        return decision.get("risk_score", decision.get("scores", {}).get("irreversible_exposure_score"))
    if field == "confidence":
        return decision.get("confidence_score", decision.get("scores", {}).get("confidence_score"))
    return None


def _controls(decision: Mapping[str, Any] | None) -> list[str]:
    if decision is None:
        return []
    values = decision.get("constraints", decision.get("controls", []))
    return [str(item) for item in values] if isinstance(values, list) else []


def _reason_codes(decision: Mapping[str, Any] | None) -> list[str]:
    if decision is None:
        return []
    values = decision.get("reason_codes", [])
    return [str(item) for item in values] if isinstance(values, list) else []


def _posture(decision_report: Mapping[str, Any]) -> str:
    decision = decision_report.get("decision")
    if isinstance(decision, dict):
        posture = str(decision.get("posture", "UNAVAILABLE")).upper()
    else:
        posture = "UNAVAILABLE"
    if posture not in VALID_POSTURES:
        raise ValueError(f"invalid SMERC posture: {posture}")
    return posture


def _safe_text(value: Any, fallback: str = "not supplied", maximum: int = 280) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    if not text:
        return fallback
    return text[:maximum]


def _env_metadata() -> Dict[str, Any]:
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "workflow": os.environ.get("GITHUB_WORKFLOW"),
        "job": os.environ.get("GITHUB_JOB"),
        "event_name": os.environ.get("GITHUB_EVENT_NAME"),
        "sha": os.environ.get("GITHUB_SHA"),
        "ref": os.environ.get("GITHUB_REF"),
        "actor": os.environ.get("GITHUB_ACTOR"),
    }


def _metadata_from_event(event_path: str | None) -> Dict[str, Any]:
    if not event_path:
        return {}
    path = Path(event_path)
    if not path.exists():
        return {}
    event = _load_json(path)
    pull_request = event.get("pull_request")
    if not isinstance(pull_request, dict):
        return {}
    return {
        "pull_request": {
            "number": pull_request.get("number"),
            "title": pull_request.get("title"),
            "user": (pull_request.get("user") or {}).get("login") if isinstance(pull_request.get("user"), dict) else None,
            "head_sha": (pull_request.get("head") or {}).get("sha") if isinstance(pull_request.get("head"), dict) else None,
            "base_ref": (pull_request.get("base") or {}).get("ref") if isinstance(pull_request.get("base"), dict) else None,
            "html_url": pull_request.get("html_url"),
        }
    }


def build_certificate(
    decision_report: Mapping[str, Any],
    *,
    action_request: Mapping[str, Any] | None = None,
    event_metadata: Mapping[str, Any] | None = None,
    issued_at: str | None = None,
) -> Dict[str, Any]:
    decision = decision_report.get("decision")
    if decision is not None and not isinstance(decision, dict):
        raise TypeError("decision_report.decision must be an object or null")
    posture = _posture(decision_report)
    certificate = {
        "version": PR_GUARDIAN_CERTIFICATE_VERSION,
        "issued_at": issued_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "posture": posture,
        "mode": decision_report.get("mode"),
        "source": decision_report.get("source"),
        "integration_status": decision_report.get("integration_status"),
        "replay_id": decision.get("replay_id") if isinstance(decision, dict) else None,
        "risk_score": _score(decision, "risk"),
        "confidence_score": _score(decision, "confidence"),
        "reason_codes": _reason_codes(decision),
        "controls": _controls(decision),
        "enforcement": dict(decision_report.get("enforcement", {})),
        "action": {
            "action_id": action_request.get("action_id") if action_request else None,
            "description": action_request.get("description") if action_request else None,
            "actor": action_request.get("actor") if action_request else None,
            "tool": action_request.get("tool") if action_request else None,
        },
        "github": dict(event_metadata or {}),
        "summary": decision.get("plain_english_summary") if isinstance(decision, dict) else (
            decision_report.get("error", {}).get("message") if isinstance(decision_report.get("error"), dict) else None
        ),
        "boundary": [
            "Pilot-grade PR evidence for review, not production certification.",
            "Does not replace branch protection, code review, security review, or deployment approvals.",
            "Customer-context pilots are required before claiming operational risk reduction.",
        ],
    }
    certificate["certificate_digest"] = _digest(certificate)
    certificate["verification"] = verify_certificate(certificate)
    return certificate


def verify_certificate(certificate: Mapping[str, Any]) -> Dict[str, Any]:
    errors: list[str] = []
    if certificate.get("version") != PR_GUARDIAN_CERTIFICATE_VERSION:
        errors.append("invalid certificate version")
    if certificate.get("posture") not in VALID_POSTURES:
        errors.append("invalid posture")
    expected = _digest(certificate)
    if certificate.get("certificate_digest") != expected:
        errors.append("certificate digest mismatch")
    return {
        "valid": not errors,
        "errors": errors,
        "certificate_digest": expected,
    }


def _posture_label(posture: str) -> str:
    labels = {
        "ALLOW": "ALLOW",
        "THROTTLE": "THROTTLE",
        "FREEZE": "FREEZE",
        "DENY": "DENY",
        "ESCALATE": "ESCALATE",
        "UNAVAILABLE": "UNAVAILABLE",
    }
    return labels[posture]


def _recommendation(posture: str, controls: list[str]) -> str:
    if posture == "ALLOW":
        return "Proceed with normal review controls and retain the decision certificate."
    if posture == "THROTTLE":
        return "Proceed only with the listed constraints before merge or deployment."
    if posture == "FREEZE":
        return "Pause automated progression until evidence or ownership gaps are resolved."
    if posture == "DENY":
        return "Do not execute this action through automation."
    if posture == "ESCALATE":
        return "Route to accountable human review before execution."
    return "No valid SMERC posture was produced; do not treat this as authorization."


def render_pr_comment(certificate: Mapping[str, Any]) -> str:
    posture = str(certificate["posture"])
    reason_codes = certificate.get("reason_codes", [])
    controls = certificate.get("controls", [])
    action = certificate.get("action", {}) if isinstance(certificate.get("action"), dict) else {}
    github = certificate.get("github", {}) if isinstance(certificate.get("github"), dict) else {}
    pull_request = github.get("pull_request", {}) if isinstance(github.get("pull_request"), dict) else {}
    lines = [
        PR_COMMENT_MARKER,
        "## SMERC PR Guardian",
        "",
        f"**Posture:** `{_posture_label(posture)}`  ",
        f"**Risk score:** `{certificate.get('risk_score')}`  ",
        f"**Confidence score:** `{certificate.get('confidence_score')}`  ",
        f"**Replay ID:** `{_safe_text(certificate.get('replay_id'))}`",
        "",
        f"**Action:** {_safe_text(action.get('description'))}",
    ]
    if pull_request.get("number"):
        lines.append(f"**Pull request:** `#{pull_request.get('number')}`")
    lines.extend(
        [
            "",
            "### Recommendation",
            "",
            _recommendation(posture, [str(item) for item in controls]),
            "",
            "### Required Controls",
            "",
        ]
    )
    if controls:
        lines.extend(f"- `{item}`" for item in controls)
    else:
        lines.append("- No additional controls returned.")
    lines.extend(["", "### Reason Codes", ""])
    if reason_codes:
        lines.extend(f"- `{item}`" for item in reason_codes)
    else:
        lines.append("- No reason codes returned.")
    lines.extend(
        [
            "",
            "### Decision Certificate",
            "",
            f"- Certificate digest: `{certificate.get('certificate_digest')}`",
            f"- Integration status: `{certificate.get('integration_status')}`",
            f"- Mode: `{certificate.get('mode')}`",
            "",
            "<sub>SMERC PR Guardian is pilot-grade evidence for review. It does not replace branch protection, code review, security review, deployment approvals, or human accountability.</sub>",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_github_output(values: Mapping[str, str]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with Path(output_path).open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key):
                handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a SMERC PR Guardian comment and certificate.")
    parser.add_argument("--decision-report", required=True, type=Path)
    parser.add_argument("--action-file", type=Path)
    parser.add_argument("--github-event-file", default=os.environ.get("GITHUB_EVENT_PATH"))
    parser.add_argument("--comment-output", type=Path, default=Path("smerc-pr-comment.md"))
    parser.add_argument("--certificate-output", type=Path, default=Path("smerc-pr-certificate.json"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    decision_report = _load_json(args.decision_report)
    action_request = _load_json(args.action_file) if args.action_file else None
    metadata = _env_metadata()
    metadata.update(_metadata_from_event(args.github_event_file))
    certificate = build_certificate(
        decision_report,
        action_request=action_request,
        event_metadata=metadata,
    )
    comment = render_pr_comment(certificate)
    args.comment_output.parent.mkdir(parents=True, exist_ok=True)
    args.certificate_output.parent.mkdir(parents=True, exist_ok=True)
    args.comment_output.write_text(comment, encoding="utf-8")
    args.certificate_output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_github_output(
        {
            "comment-file": str(args.comment_output),
            "certificate-file": str(args.certificate_output),
            "certificate-digest": str(certificate["certificate_digest"]),
            "posture": str(certificate["posture"]),
        }
    )
    print(json.dumps(certificate, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

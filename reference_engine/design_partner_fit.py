from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc.design-partner-fit.v1"
CATEGORIES = [
    "workflow_fit",
    "recoverability_pain",
    "metadata_readiness",
    "reviewer_capacity",
    "buyer_ownership",
    "data_boundary",
    "measurement_readiness",
    "pilot_urgency",
]


FIT_BANDS = [
    (0, 8, "weak", "Do not pursue a paid pilot. Offer public materials only."),
    (9, 15, "exploratory", "Offer a CISO Technical Review, free to $2,500."),
    (16, 21, "moderate", "Offer a 30-Day Shadow-Mode Pilot, $7,500-$15,000, if reviewer time is confirmed."),
    (22, 24, "strong", "Offer a 90-Day Design Partner Pilot, $25,000-$50,000, with DLL evidence package."),
]


def _require_text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _require_score(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{path} must be an integer")
    if not 0 <= value <= 3:
        raise ValueError(f"{path} must be between 0 and 3")
    return value


def validate_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {"schema", "organization", "assessment_date", "notes", "scores", "evidence"}
    unknown = sorted(set(payload) - required)
    missing = sorted(required - set(payload))
    if unknown:
        raise ValueError(f"design partner fit payload contains unknown field(s): {', '.join(unknown)}")
    if missing:
        raise ValueError(f"design partner fit payload is missing field(s): {', '.join(missing)}")
    if payload["schema"] != VERSION:
        raise ValueError(f"schema must be {VERSION}")
    scores = payload["scores"]
    evidence = payload["evidence"]
    if not isinstance(scores, dict):
        raise TypeError("scores must be an object")
    if not isinstance(evidence, dict):
        raise TypeError("evidence must be an object")
    score_unknown = sorted(set(scores) - set(CATEGORIES))
    score_missing = sorted(set(CATEGORIES) - set(scores))
    evidence_unknown = sorted(set(evidence) - set(CATEGORIES))
    evidence_missing = sorted(set(CATEGORIES) - set(evidence))
    if score_unknown or evidence_unknown:
        raise ValueError("scores and evidence must use only declared fit categories")
    if score_missing or evidence_missing:
        raise ValueError("scores and evidence must include every declared fit category")
    return {
        "schema": VERSION,
        "organization": _require_text(payload["organization"], "organization"),
        "assessment_date": _require_text(payload["assessment_date"], "assessment_date"),
        "notes": _require_text(payload["notes"], "notes"),
        "scores": {category: _require_score(scores[category], f"scores.{category}") for category in CATEGORIES},
        "evidence": {category: _require_text(evidence[category], f"evidence.{category}") for category in CATEGORIES},
    }


def fit_band(total_score: int) -> Dict[str, str]:
    for minimum, maximum, label, recommendation in FIT_BANDS:
        if minimum <= total_score <= maximum:
            return {"fit": label, "recommendation": recommendation}
    raise ValueError("total score is outside expected range")


def assess(payload: Mapping[str, Any]) -> Dict[str, Any]:
    parsed = validate_payload(payload)
    total_score = sum(parsed["scores"].values())
    band = fit_band(total_score)
    blockers = blockers_for(parsed["scores"])
    return {
        "schema": VERSION,
        "organization": parsed["organization"],
        "assessment_date": parsed["assessment_date"],
        "notes": parsed["notes"],
        "total_score": total_score,
        "maximum_score": len(CATEGORIES) * 3,
        "fit": band["fit"],
        "recommendation": band["recommendation"],
        "blockers": blockers,
        "scores": parsed["scores"],
        "evidence": parsed["evidence"],
        "evidence_boundary": "Qualification screen only; not proof of buyer intent, product-market fit, or pilot success.",
    }


def blockers_for(scores: Mapping[str, int]) -> list[str]:
    blockers = []
    if scores["reviewer_capacity"] == 0:
        blockers.append("No reviewer capacity. Do not run a paid pilot.")
    if scores["data_boundary"] <= 1:
        blockers.append("Data boundary is not safe enough for a metadata-only first pilot.")
    if scores["workflow_fit"] == 0:
        blockers.append("No meaningful side-effecting workflow is available.")
    if scores["buyer_ownership"] == 0:
        blockers.append("No buyer or accountable sponsor identified.")
    if scores["measurement_readiness"] == 0:
        blockers.append("No measurable success path.")
    return blockers


def load_payload(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("design partner fit file must contain a JSON object")
    return payload


def markdown(report: Mapping[str, Any]) -> str:
    lines = [
        f"# {report['organization']} Design Partner Fit Assessment",
        "",
        f"Assessment date: {report['assessment_date']}",
        "",
        "## Result",
        "",
        f"- Total score: `{report['total_score']}` of `{report['maximum_score']}`",
        f"- Fit band: `{report['fit']}`",
        f"- Recommendation: {report['recommendation']}",
        "",
        "## Blockers",
        "",
    ]
    if report["blockers"]:
        lines.extend(f"- {blocker}" for blocker in report["blockers"])
    else:
        lines.append("- None identified by this screen.")
    lines.extend(
        [
            "",
            "## Scores",
            "",
            "| Category | Score | Evidence |",
            "| --- | ---: | --- |",
        ]
    )
    for category in CATEGORIES:
        lines.append(
            f"| `{category}` | {report['scores'][category]} | {safe(report['evidence'][category])} |"
        )
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            str(report["evidence_boundary"]),
        ]
    )
    return "\n".join(lines) + "\n"


def safe(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Score SMERC design-partner pilot fit.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = assess(load_payload(args.path))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


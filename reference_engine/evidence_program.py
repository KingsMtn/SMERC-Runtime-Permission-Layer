from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from reference_engine.evidence_provenance import hmac_key_from_env, verify_ledger


PROGRAM_VERSION = "smerc.evidence-program.v1"
REPORT_VERSION = "smerc.evidence-report.v1"
RISK_LEVELS = {"critical", "high", "moderate"}
UNKNOWN_CLASSES = {"epistemic", "adversarial", "operational", "normative", "commercial", "regulatory"}
OPERATORS = {"gte", "lte"}
CEILING_RANK = {"STOP": 0, "OBSERVE": 1, "RECOMMEND": 2, "LIMITED_ENFORCE": 3, "CALIBRATED_ENFORCE": 4}


def _object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    return value


def _list(value: Any, path: str, *, allow_empty: bool = False) -> List[Any]:
    if not isinstance(value, list) or (not allow_empty and not value):
        suffix = "" if allow_empty else " with at least one item"
        raise TypeError(f"{path} must be an array{suffix}")
    return value


def _text(value: Any, path: str, maximum: int = 1000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value.strip()


def _number(value: Any, path: str, *, minimum: float = 0.0, maximum: float = 1.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number")
    if not minimum <= value <= maximum:
        raise ValueError(f"{path} must be between {minimum} and {maximum}")
    return float(value)


def _integer(value: Any, path: str, *, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{path} must be an integer of at least {minimum}")
    return value


def _timestamp(value: str, path: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{path} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{path} must include a timezone")
    return parsed


def _exact_fields(value: Dict[str, Any], required: Iterable[str], path: str) -> None:
    required_set = set(required)
    missing = sorted(required_set - set(value))
    unknown = sorted(set(value) - required_set)
    if missing:
        raise ValueError(f"{path} is missing field(s): {', '.join(missing)}")
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def validate_program(payload: Dict[str, Any]) -> Dict[str, Any]:
    program = _object(payload, "program")
    _exact_fields(program, {"version", "program_id", "title", "claims"}, "program")
    if program["version"] != PROGRAM_VERSION:
        raise ValueError(f"program.version must be {PROGRAM_VERSION}")
    _text(program["program_id"], "program.program_id", 128)
    _text(program["title"], "program.title", 256)
    claims = _list(program["claims"], "program.claims")
    claim_ids = set()
    criterion_ids = set()
    for index, raw_claim in enumerate(claims):
        path = f"program.claims[{index}]"
        claim = _object(raw_claim, path)
        _exact_fields(
            claim,
            {"claim_id", "statement", "unknown_class", "risk_level", "owner_role", "failure_consequence", "criteria"},
            path,
        )
        claim_id = _text(claim["claim_id"], f"{path}.claim_id", 64)
        if claim_id in claim_ids:
            raise ValueError(f"Duplicate claim_id: {claim_id}")
        claim_ids.add(claim_id)
        _text(claim["statement"], f"{path}.statement")
        if claim["unknown_class"] not in UNKNOWN_CLASSES:
            raise ValueError(f"{path}.unknown_class is not recognized")
        if claim["risk_level"] not in RISK_LEVELS:
            raise ValueError(f"{path}.risk_level is not recognized")
        _text(claim["owner_role"], f"{path}.owner_role", 128)
        _text(claim["failure_consequence"], f"{path}.failure_consequence")
        for criterion_index, raw_criterion in enumerate(_list(claim["criteria"], f"{path}.criteria")):
            criterion_path = f"{path}.criteria[{criterion_index}]"
            criterion = _object(raw_criterion, criterion_path)
            _exact_fields(
                criterion,
                {"criterion_id", "metric", "operator", "threshold", "minimum_sample_size", "minimum_source_quality", "required_segments"},
                criterion_path,
            )
            criterion_id = _text(criterion["criterion_id"], f"{criterion_path}.criterion_id", 64)
            if criterion_id in criterion_ids:
                raise ValueError(f"Duplicate criterion_id: {criterion_id}")
            criterion_ids.add(criterion_id)
            _text(criterion["metric"], f"{criterion_path}.metric", 128)
            if criterion["operator"] not in OPERATORS:
                raise ValueError(f"{criterion_path}.operator must be gte or lte")
            _number(criterion["threshold"], f"{criterion_path}.threshold", minimum=-1_000_000, maximum=1_000_000)
            _integer(criterion["minimum_sample_size"], f"{criterion_path}.minimum_sample_size")
            _number(criterion["minimum_source_quality"], f"{criterion_path}.minimum_source_quality")
            segments = _list(criterion["required_segments"], f"{criterion_path}.required_segments", allow_empty=True)
            for segment_index, segment in enumerate(segments):
                _text(segment, f"{criterion_path}.required_segments[{segment_index}]", 128)
    return program


def validate_observations(payload: Any, criteria: Dict[str, tuple[str, str]]) -> List[Dict[str, Any]]:
    observations = _list(payload, "observations", allow_empty=True)
    observation_ids = set()
    for index, raw_observation in enumerate(observations):
        path = f"observations[{index}]"
        observation = _object(raw_observation, path)
        _exact_fields(
            observation,
            {"observation_id", "claim_id", "criterion_id", "metric", "value", "sample_size", "source_quality", "segments", "source_type", "dataset_id", "collected_at"},
            path,
        )
        observation_id = _text(observation["observation_id"], f"{path}.observation_id", 128)
        if observation_id in observation_ids:
            raise ValueError(f"Duplicate observation_id: {observation_id}")
        observation_ids.add(observation_id)
        if observation["claim_id"] not in {item[0] for item in criteria.values()}:
            raise ValueError(f"{path}.claim_id does not exist in the program")
        for field in ("criterion_id", "metric", "source_type", "dataset_id", "collected_at"):
            _text(observation[field], f"{path}.{field}", 256)
        expected = criteria.get(observation["criterion_id"])
        if expected is None:
            raise ValueError(f"{path}.criterion_id does not exist in the program")
        if expected != (observation["claim_id"], observation["metric"]):
            raise ValueError(f"{path} does not match the criterion's claim and metric")
        _timestamp(observation["collected_at"], f"{path}.collected_at")
        _number(observation["value"], f"{path}.value", minimum=-1_000_000, maximum=1_000_000)
        _integer(observation["sample_size"], f"{path}.sample_size")
        _number(observation["source_quality"], f"{path}.source_quality")
        for segment_index, segment in enumerate(_list(observation["segments"], f"{path}.segments", allow_empty=True)):
            _text(segment, f"{path}.segments[{segment_index}]", 128)
    return observations


def _criterion_result(criterion: Dict[str, Any], observations: List[Dict[str, Any]]) -> Dict[str, Any]:
    matching = [
        item for item in observations
        if item["criterion_id"] == criterion["criterion_id"] and item["metric"] == criterion["metric"]
    ]
    qualified = [
        item for item in matching
        if item["sample_size"] >= criterion["minimum_sample_size"]
        and item["source_quality"] >= criterion["minimum_source_quality"]
        and set(criterion["required_segments"]).issubset(set(item["segments"]))
    ]
    if not qualified:
        return {"criterion_id": criterion["criterion_id"], "status": "INSUFFICIENT", "qualified_observations": 0, "latest_value": None}
    latest = sorted(qualified, key=lambda item: _timestamp(item["collected_at"], "observation.collected_at"))[-1]
    outcomes = [
        item["value"] >= criterion["threshold"]
        if criterion["operator"] == "gte"
        else item["value"] <= criterion["threshold"]
        for item in qualified
    ]
    status = "CONFLICTED" if any(outcomes) and not all(outcomes) else ("SUPPORTED" if all(outcomes) else "CHALLENGED")
    return {
        "criterion_id": criterion["criterion_id"],
        "status": status,
        "qualified_observations": len(qualified),
        "latest_value": latest["value"],
        "threshold": criterion["threshold"],
        "operator": criterion["operator"],
        "dataset_id": latest["dataset_id"],
    }


def _claim_status(criteria: List[Dict[str, Any]]) -> str:
    statuses = {item["status"] for item in criteria}
    if "CHALLENGED" in statuses:
        return "CHALLENGED"
    if "CONFLICTED" in statuses:
        return "CONFLICTED"
    if statuses == {"SUPPORTED"}:
        return "SUPPORTED"
    if "SUPPORTED" in statuses:
        return "PARTIAL"
    return "UNTESTED"


def _deployment_ceiling(results: List[Dict[str, Any]]) -> tuple[str, List[str]]:
    challenged_critical = [item["claim_id"] for item in results if item["risk_level"] == "critical" and item["status"] in {"CHALLENGED", "CONFLICTED"}]
    if challenged_critical:
        return "STOP", challenged_critical
    unresolved_critical = [item["claim_id"] for item in results if item["risk_level"] == "critical" and item["status"] != "SUPPORTED"]
    if unresolved_critical:
        return "OBSERVE", unresolved_critical
    challenged_high = [item["claim_id"] for item in results if item["risk_level"] == "high" and item["status"] in {"CHALLENGED", "CONFLICTED"}]
    if challenged_high:
        return "OBSERVE", challenged_high
    unresolved_high = [item["claim_id"] for item in results if item["risk_level"] == "high" and item["status"] != "SUPPORTED"]
    if unresolved_high:
        return "RECOMMEND", unresolved_high
    unresolved_moderate = [item["claim_id"] for item in results if item["risk_level"] == "moderate" and item["status"] != "SUPPORTED"]
    if unresolved_moderate:
        return "LIMITED_ENFORCE", unresolved_moderate
    return "CALIBRATED_ENFORCE", []


def evaluate_evidence(
    program_payload: Dict[str, Any],
    observation_payload: Any,
    *,
    provenance_ledger: Optional[Dict[str, Any]] = None,
    provenance_hmac_key: Optional[bytes] = None,
) -> Dict[str, Any]:
    program = validate_program(program_payload)
    criteria = {
        criterion["criterion_id"]: (claim["claim_id"], criterion["metric"])
        for claim in program["claims"] for criterion in claim["criteria"]
    }
    observations = validate_observations(observation_payload, criteria)
    if provenance_ledger is None:
        provenance = {
            "status": "NO_OBSERVATIONS" if not observations else "UNVERIFIED",
            "record_count": 0,
            "head_record_hash": None,
        }
    else:
        provenance = verify_ledger(observations, provenance_ledger, hmac_key=provenance_hmac_key)
        if provenance["program_id"] != program["program_id"]:
            raise ValueError("Evidence ledger program_id does not match the evidence program")
    results = []
    for claim in program["claims"]:
        claim_observations = [item for item in observations if item["claim_id"] == claim["claim_id"]]
        criteria = [_criterion_result(criterion, claim_observations) for criterion in claim["criteria"]]
        results.append({
            "claim_id": claim["claim_id"], "statement": claim["statement"],
            "unknown_class": claim["unknown_class"], "risk_level": claim["risk_level"],
            "status": _claim_status(criteria), "owner_role": claim["owner_role"],
            "failure_consequence": claim["failure_consequence"], "criteria": criteria,
        })
    evidence_ceiling, blockers = _deployment_ceiling(results)
    provenance_cap = {
        "UNVERIFIED": "OBSERVE",
        "HASH_VERIFIED": "RECOMMEND",
    }.get(provenance["status"])
    ceiling = evidence_ceiling
    if provenance_cap and CEILING_RANK[ceiling] > CEILING_RANK[provenance_cap]:
        ceiling = provenance_cap
    return {
        "version": REPORT_VERSION,
        "program_id": program["program_id"],
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "deployment_ceiling": ceiling,
        "evidence_based_ceiling": evidence_ceiling,
        "provenance": provenance,
        "provenance_cap_applied": ceiling != evidence_ceiling,
        "blocking_claim_ids": blockers,
        "claim_counts": dict(Counter(item["status"] for item in results)),
        "unknown_class_counts": dict(Counter(item["unknown_class"] for item in results if item["status"] != "SUPPORTED")),
        "claims": results,
        "interpretation": "The deployment ceiling is an evidence gate, not a production certification or safety guarantee.",
    }


def markdown_report(report: Dict[str, Any]) -> str:
    lines = [
        "# SMERC Evidence And Unknowns Report", "",
        f"- Program: `{report['program_id']}`",
        f"- Evaluated: `{report['evaluated_at']}`",
        f"- Evidence-limited deployment ceiling: **{report['deployment_ceiling']}**", "",
        f"- Evidence-only ceiling: **{report['evidence_based_ceiling']}**",
        f"- Provenance status: **{report['provenance']['status']}**", "",
        "> This ceiling is an evidence gate, not a production certification or safety guarantee.", "",
        "## Claim Status", "", "| Claim | Risk | Unknown class | Status |", "| --- | --- | --- | --- |",
    ]
    for claim in report["claims"]:
        lines.append(f"| `{claim['claim_id']}` | {claim['risk_level']} | {claim['unknown_class']} | **{claim['status']}** |")
    lines.extend(["", "## Deployment Blockers", ""])
    if report["blocking_claim_ids"]:
        lines.extend(f"- `{claim_id}`" for claim_id in report["blocking_claim_ids"])
    else:
        lines.append("- No unresolved claims limit the current evidence ceiling.")
    lines.extend(["", "## Interpretation", "", report["interpretation"], ""])
    return "\n".join(lines)


def write_report(report: Dict[str, Any], json_output: Optional[Path], markdown_output: Optional[Path]) -> None:
    if json_output:
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if markdown_output:
        markdown_output.parent.mkdir(parents=True, exist_ok=True)
        markdown_output.write_text(markdown_report(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the SMERC evidence and unknowns program")
    parser.add_argument("program", type=Path)
    parser.add_argument("observations", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--hmac-key-env")
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8")) if args.ledger else None
    report = evaluate_evidence(
        json.loads(args.program.read_text(encoding="utf-8")),
        json.loads(args.observations.read_text(encoding="utf-8")),
        provenance_ledger=ledger,
        provenance_hmac_key=hmac_key_from_env(args.hmac_key_env),
    )
    write_report(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

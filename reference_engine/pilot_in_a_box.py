from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.customer_evaluation import build_customer_evaluation, load_payload, write_outputs
from reference_engine.customer_proof_loop import build_customer_proof_loop, write_customer_proof_loop


PILOT_IN_A_BOX_VERSION = "smerc.pilot-in-a-box.v1"

DEFAULT_EVALUATION_PACKS = {
    "general_ai_agent": Path("examples/customer_eval_actions.json"),
    "cloud_admin": Path("examples/cloud_admin_customer_eval_actions.json"),
    "financial_runtime": Path("examples/smerc_f_customer_eval_actions.json"),
}
DEFAULT_PROOF_ACTION = Path("examples/customer_proof_action.json")


def build_pilot_in_a_box(
    *,
    root: Path,
    output_dir: Path,
    evaluation_packs: Mapping[str, Path] | None = None,
    proof_action: Path = DEFAULT_PROOF_ACTION,
) -> Dict[str, Any]:
    packs = evaluation_packs or DEFAULT_EVALUATION_PACKS
    generated_at = _now()
    package_dir = output_dir
    evaluation_results = []

    for name, relative_path in packs.items():
        source_path = root / relative_path
        report = build_customer_evaluation(load_payload(source_path))
        pack_dir = package_dir / name
        json_output = pack_dir / "customer_evaluation_report.json"
        markdown_output = pack_dir / "Customer_Evaluation_Report.md"
        write_outputs(report, json_output, markdown_output)
        evaluation_results.append(
            {
                "name": name,
                "source": _rel(source_path, root),
                "json_report": _rel(json_output, root),
                "markdown_report": _rel(markdown_output, root),
                "summary": report["summary"],
                "pilot_fit": report["pilot_fit"],
                "recommended_next_action": report["recommended_next_action"],
            }
        )

    proof_source = root / proof_action
    proof_report = build_customer_proof_loop(json.loads(proof_source.read_text(encoding="utf-8")))
    proof_paths = write_customer_proof_loop(proof_report, package_dir / "single_action_proof_loop")
    proof_result = {
        "source": _rel(proof_source, root),
        "json_report": _rel(Path(proof_paths["json"]), root),
        "markdown_report": _rel(Path(proof_paths["markdown"]), root),
        "summary": proof_report["summary"],
    }

    summary = _summarize(evaluation_results)
    manifest = {
        "version": PILOT_IN_A_BOX_VERSION,
        "generated_at": generated_at,
        "purpose": "One-command, metadata-only SMERC pilot preview for company reviewers.",
        "evidence_boundary": (
            "This package uses synthetic or reviewer-supplied metadata only. It demonstrates runtime coherence, "
            "report generation, recoverability postures, SPARTa routes, Decision Lifecycle Ledger evidence, and "
            "pilot-fit signals. It does not prove production safety, compliance, incident reduction, customer demand, "
            "or enforce-mode readiness."
        ),
        "recommended_reviewer_flow": [
            "Read Pilot_In_A_Box_Report.md.",
            "Open the strongest-fit evaluation report.",
            "Replace one example pack with 5 to 25 metadata-only actions from one owned workflow.",
            "Compare SMERC posture against current reviewer judgment.",
            "Move to shadow mode only if reviewers find a useful difference.",
        ],
        "summary": summary,
        "evaluation_results": evaluation_results,
        "single_action_proof_loop": proof_result,
    }
    _write_manifest(root, package_dir, manifest)
    return manifest


def render_markdown(manifest: Mapping[str, Any]) -> str:
    summary = manifest["summary"]
    comparison = summary["binary_policy_comparison"]
    lines = [
        "# SMERC Pilot-In-A-Box Report",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## What This Is",
        "",
        (
            "This is a one-command, metadata-only pilot preview. It runs SMERC across general AI-agent, "
            "cloud-admin, and financial-runtime action packs, then produces reviewer-ready evidence."
        ),
        "",
        "## Evidence Boundary",
        "",
        str(manifest["evidence_boundary"]),
        "",
        "## Result",
        "",
        f"- Evaluation packs: `{summary['evaluation_pack_count']}`",
        f"- Actions evaluated: `{summary['total_actions']}`",
        f"- Non-executable routes: `{summary['non_executable_routes']}`",
        f"- Valid DLL ledgers: `{summary['valid_ledgers']}`",
        f"- Strong pilot-fit packs: `{summary['strong_pilot_fit_packs']}`",
        f"- Moderate pilot-fit packs: `{summary['moderate_pilot_fit_packs']}`",
        f"- Posture counts: `{summary['posture_counts']}`",
        f"- Route state counts: `{summary['route_state_counts']}`",
        f"- Actions constrained instead of simply allowed or blocked: `{comparison['constrained_actions']}`",
        f"- Binary-equivalent allow count: `{comparison['binary_equivalent_allow']}`",
        f"- Binary-equivalent block/review count: `{comparison['binary_equivalent_block_or_review']}`",
        "",
        "## SMERC Versus Binary Allow/Block",
        "",
        (
            "A traditional binary control usually has to choose between allowing useful automation and blocking it. "
            "SMERC adds middle states when an action is technically possible but needs scope limits, checkpoints, "
            "rollback evidence, or human review before execution."
        ),
        "",
        "| Signal | Count | Why It Matters |",
        "| --- | ---: | --- |",
        f"| `ALLOW` | {comparison['allow_actions']} | Low-risk actions can keep moving. |",
        f"| `THROTTLE` | {comparison['constrained_actions']} | Useful actions are constrained instead of treated as all-or-nothing. |",
        f"| `FREEZE/ESCALATE/DENY` | {comparison['blocked_or_held_actions']} | Poorly recoverable or poorly evidenced actions stop before execution. |",
        f"| `DLL_VALID` | {summary['valid_ledgers']} | Decisions produce replayable governance evidence. |",
        "",
        "## Evaluation Packs",
        "",
        "| Pack | Source | Pilot Fit | Actions | Non-Executable | Markdown Report |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for result in manifest["evaluation_results"]:
        pack_summary = result["summary"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{result['name']}`",
                    f"`{result['source']}`",
                    f"`{result['pilot_fit']['fit']}`",
                    str(pack_summary["total_actions"]),
                    str(pack_summary["non_executable_routes"]),
                    f"`{result['markdown_report']}`",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Single-Action Proof Loop",
            "",
            f"- Source: `{manifest['single_action_proof_loop']['source']}`",
            f"- Markdown report: `{manifest['single_action_proof_loop']['markdown_report']}`",
            f"- Overall status: `{manifest['single_action_proof_loop']['summary']['overall_status']}`",
            "",
            "## Recommended Reviewer Flow",
            "",
        ]
    )
    lines.extend(f"{index}. {step}" for index, step in enumerate(manifest["recommended_reviewer_flow"], start=1))
    lines.extend(
        [
            "",
            "## Work, Result, Impact",
            "",
            "- Work: SMERC evaluates metadata-only action packs through hard evidence gates, recoverability scoring, SPARTa routing, autonomy impact, and Decision Lifecycle Ledger evidence.",
            "- Result: A reviewer receives concrete reports instead of a slide-only explanation.",
            "- Impact: A company can decide whether a shadow-mode pilot is worth time before sharing sensitive data or granting execution authority.",
            "",
        ]
    )
    return "\n".join(lines)


def write_pilot_in_a_box(manifest: Mapping[str, Any], root: Path, output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "pilot_in_a_box_manifest.json"
    markdown_path = output_dir / "Pilot_In_A_Box_Report.md"
    json_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(manifest), encoding="utf-8")
    return {"json": _rel(json_path, root), "markdown": _rel(markdown_path, root)}


def _write_manifest(root: Path, output_dir: Path, manifest: Dict[str, Any]) -> None:
    paths = write_pilot_in_a_box(manifest, root, output_dir)
    manifest["manifest_paths"] = paths
    json_path = root / paths["json"]
    json_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _summarize(evaluation_results: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    results = list(evaluation_results)
    posture_counts: Counter[str] = Counter()
    route_counts: Counter[str] = Counter()
    total_actions = 0
    non_executable = 0
    valid_ledgers = 0
    strong = 0
    moderate = 0
    for result in results:
        summary = result["summary"]
        total_actions += int(summary["total_actions"])
        non_executable += int(summary["non_executable_routes"])
        valid_ledgers += int(summary["valid_ledgers"])
        posture_counts.update(summary["posture_counts"])
        route_counts.update(summary["route_state_counts"])
        fit = result["pilot_fit"]["fit"]
        strong += int(fit == "strong")
        moderate += int(fit == "moderate")
    binary_comparison = {
        "allow_actions": posture_counts.get("ALLOW", 0),
        "constrained_actions": posture_counts.get("THROTTLE", 0),
        "blocked_or_held_actions": (
            posture_counts.get("FREEZE", 0)
            + posture_counts.get("DENY", 0)
            + posture_counts.get("ESCALATE", 0)
        ),
        "binary_equivalent_allow": posture_counts.get("ALLOW", 0) + posture_counts.get("THROTTLE", 0),
        "binary_equivalent_block_or_review": (
            posture_counts.get("FREEZE", 0)
            + posture_counts.get("DENY", 0)
            + posture_counts.get("ESCALATE", 0)
        ),
        "interpretation": (
            "THROTTLE is the visible delta: these actions are not simply allowed or blocked; "
            "they proceed only with controls such as scope limits, checkpoints, rollback plans, or review routing."
        ),
    }
    return {
        "evaluation_pack_count": len(results),
        "total_actions": total_actions,
        "non_executable_routes": non_executable,
        "valid_ledgers": valid_ledgers,
        "strong_pilot_fit_packs": strong,
        "moderate_pilot_fit_packs": moderate,
        "posture_counts": dict(sorted(posture_counts.items())),
        "route_state_counts": dict(sorted(route_counts.items())),
        "binary_policy_comparison": binary_comparison,
    }


def _rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the SMERC pilot-in-a-box reviewer package.")
    parser.add_argument("--output-dir", default="reports/pilot_in_a_box")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    root = Path.cwd()
    manifest = build_pilot_in_a_box(root=root, output_dir=Path(args.output_dir))
    print(json.dumps(manifest if args.pretty else {"summary": manifest["summary"], "paths": manifest["manifest_paths"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

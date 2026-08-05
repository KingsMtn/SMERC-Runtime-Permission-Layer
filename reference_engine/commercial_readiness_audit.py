from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence


VERSION = "smerc.commercial-readiness-audit.v1"

DEFAULT_PUBLIC_FILES = [
    "README.md",
    "COMMUNITY.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/Plain_English_Product_Overview.md",
    "docs/Public_Review_Snapshot.md",
    "docs/CISO_30_Minute_Review_Package.md",
    "docs/CISO_GitHub_Inspection_Guide.md",
    "docs/CISO_Quick_Review.md",
    "docs/Maturity_Model.md",
    "docs/Partner_Program.md",
    "docs/Community_Outreach_Kit.md",
    "docs/Findability_And_AI_Discovery.md",
    "docs/Naming_And_Search_Style_Guide.md",
    "pilot_package/Level_5_Shadow_Mode_Pilot_Packet.md",
    "pilot_package/Pricing_And_Pilot_Evidence_Position.md",
]

REQUIRED_POSITIONING_TERMS = [
    "runtime permission",
    "recoverability",
    "shadow-mode",
    "not production-certified",
]

RISKY_CLAIM_PATTERNS = [
    (r"\bguarantee[sd]?\b", "Avoid guaranteed outcomes unless backed by a contract or formal assurance."),
    (r"\bworld['’]?s first\b", "Avoid novelty claims unless patent/prior-art counsel has cleared them."),
    (r"\bfirst ever\b", "Avoid broad novelty claims unless patent/prior-art counsel has cleared them."),
    (r"\bbest[- ]in[- ]class\b", "Avoid unsupported comparative superiority claims."),
    (r"\brevolutionary\b", "Replace broad promotional language with concrete capabilities."),
    (r"\bbulletproof\b", "Avoid absolute safety language."),
    (r"\bunbreakable\b", "Avoid absolute safety language."),
    (r"\beliminates? risk\b", "Use risk-reduction or evidence-bound language instead of elimination claims."),
    (r"\bprevents? all\b", "Avoid absolute prevention claims."),
    (r"\bproduction[- ]certified\b", "Do not imply certification unless an external certification exists."),
    (r"\bproven to reduce incidents\b", "Only claim incident reduction after live customer evidence exists."),
]


def audit_repository(root: Path, public_files: Sequence[str] | None = None) -> Dict[str, Any]:
    repo = root.resolve()
    if not repo.exists() or not repo.is_dir():
        raise FileNotFoundError(f"repository directory does not exist: {root}")

    files = list(public_files or DEFAULT_PUBLIC_FILES)
    findings: List[Dict[str, str]] = []
    texts: Dict[str, str] = {}

    for relative in files:
        path = repo / relative
        if not path.exists():
            findings.append(
                _finding("missing_public_file", relative, "Expected public review file is missing.", severity="warning")
            )
            continue
        texts[relative] = path.read_text(encoding="utf-8")

    _check_required_positioning(texts, findings)
    _check_risky_claims(texts, findings)
    _check_readme_evidence_boundary(texts.get("README.md", ""), findings)

    blocking = [item for item in findings if item["severity"] == "blocking"]
    warning = [item for item in findings if item["severity"] == "warning"]
    return {
        "schema": VERSION,
        "repository_dir": str(repo),
        "passed": not blocking,
        "blocking_count": len(blocking),
        "warning_count": len(warning),
        "files_checked": files,
        "required_positioning_terms": REQUIRED_POSITIONING_TERMS,
        "findings": findings,
        "evidence_boundary": (
            "Commercial-readiness language audit only; it does not prove legal clearance, "
            "security certification, buyer demand, product-market fit, or production suitability."
        ),
    }


def _check_required_positioning(texts: Mapping[str, str], findings: List[Dict[str, str]]) -> None:
    combined = "\n".join(texts.values()).lower()
    for term in REQUIRED_POSITIONING_TERMS:
        if term.lower() not in combined:
            findings.append(
                _finding(
                    "missing_positioning_term",
                    "public_materials",
                    f"Public materials should include the boundary term `{term}`.",
                    severity="blocking",
                )
            )


def _check_risky_claims(texts: Mapping[str, str], findings: List[Dict[str, str]]) -> None:
    for relative, text in texts.items():
        for pattern, guidance in RISKY_CLAIM_PATTERNS:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                line_number = text.count("\n", 0, match.start()) + 1
                snippet = _line_for(text, match.start())
                if _is_cautionary_language(snippet):
                    continue
                findings.append(
                    _finding(
                        "risky_claim_language",
                        f"{relative}:{line_number}",
                        f"{guidance} Found: `{snippet}`",
                        severity="warning",
                    )
                )


def _check_readme_evidence_boundary(readme: str, findings: List[Dict[str, str]]) -> None:
    lower = readme.lower()
    checks = {
        "not production-certified": "not production-certified" in lower,
        "shadow-mode pilot": "shadow-mode pilot" in lower,
        "not proven to reduce incidents": bool(
            re.search(r"not[^.\n]{0,140}proven to reduce incidents", lower)
            or "not proven to reduce incidents" in lower
            or "without live customer evidence" in lower
        ),
    }
    for fragment, present in checks.items():
        if not present:
            findings.append(
                _finding(
                    "readme_missing_evidence_boundary",
                    "README.md",
                    f"README should state `{fragment}` or equivalent evidence boundary.",
                    severity="blocking",
                )
            )


def _line_for(text: str, index: int) -> str:
    start = text.rfind("\n", 0, index) + 1
    end = text.find("\n", index)
    if end == -1:
        end = len(text)
    return re.sub(r"\s+", " ", text[start:end]).strip()[:180]


def _is_cautionary_language(line: str) -> bool:
    normalized = line.lower()
    caution_markers = [
        "not ",
        "not yet",
        "not currently",
        "should not",
        "does not",
        "do not",
        "without",
        "avoid ",
        "unsupported",
        "only after",
        "no guarantee",
        "not sold as",
    ]
    return any(marker in normalized for marker in caution_markers)


def _finding(code: str, target: str, message: str, *, severity: str = "warning") -> Dict[str, str]:
    return {
        "severity": severity,
        "code": code,
        "target": target,
        "message": message,
    }


def markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Commercial Readiness Language Audit",
        "",
        f"- Passed: `{str(report['passed']).lower()}`",
        f"- Blocking findings: `{report['blocking_count']}`",
        f"- Warnings: `{report['warning_count']}`",
        f"- Repository directory: `{report['repository_dir']}`",
        "",
        "## What This Checks",
        "",
        "- Public-facing materials use runtime-permission and recoverability positioning.",
        "- Public-facing materials preserve the shadow-mode and not-production-certified boundary.",
        "- Public-facing materials avoid unsupported novelty, superiority, guarantee, and certification claims.",
        "",
        "## Findings",
        "",
    ]
    if report["findings"]:
        lines.extend(
            f"- `{item['severity']}` `{item['code']}` `{item['target']}`: {item['message']}"
            for item in report["findings"]
        )
    else:
        lines.append("- None.")
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"])])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SMERC public materials for commercial-readiness language risk.")
    parser.add_argument("repository_dir", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = audit_repository(args.repository_dir)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

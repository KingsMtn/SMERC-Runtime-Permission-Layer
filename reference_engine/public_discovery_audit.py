from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping


VERSION = "smerc.public-discovery-audit.v1"
REQUIRED_FILES = [
    "index.html",
    "ai-agent-governance.html",
    "llms.txt",
    "sitemap.xml",
    "project.json",
    "smerc-beacon.json",
    ".well-known/smerc.json",
]
REQUIRED_TERMS = [
    "SMERC",
    "Structural Momentum Entropy Range Confidence",
    "runtime permission",
    "AI agent governance",
    "recoverability scoring",
]
EXPECTED_HOME_TITLE = "SMERC | Runtime Permission Infrastructure for AI Agents"
EXPECTED_TAGLINE = "Recoverability scoring before automated actions execute."


def audit_site(site_dir: Path) -> Dict[str, Any]:
    root = site_dir.resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"site directory does not exist: {site_dir}")

    findings: List[Dict[str, str]] = []
    files = {relative: root / relative for relative in REQUIRED_FILES}
    for relative, path in files.items():
        if not path.exists():
            findings.append(_finding("missing_file", relative, "Required public discovery file is missing."))

    texts = {relative: _read(path) for relative, path in files.items() if path.exists()}
    json_payloads = _load_json_payloads(root, findings)

    _check_title(texts, findings)
    _check_terms(texts, findings)
    _check_sitemap(texts.get("sitemap.xml", ""), findings)
    _check_project_json(json_payloads.get("project.json"), findings)
    _check_beacon("smerc-beacon.json", json_payloads.get("smerc-beacon.json"), findings)
    _check_beacon(".well-known/smerc.json", json_payloads.get(".well-known/smerc.json"), findings)

    blocking = [item for item in findings if item["severity"] == "blocking"]
    warning = [item for item in findings if item["severity"] == "warning"]
    return {
        "schema": VERSION,
        "site_dir": str(root),
        "passed": not blocking,
        "blocking_count": len(blocking),
        "warning_count": len(warning),
        "findings": findings,
        "required_files": REQUIRED_FILES,
        "required_terms": REQUIRED_TERMS,
        "evidence_boundary": "Local site-export audit only; it does not prove search indexing, ranking, crawler ingestion, or product-market fit.",
    }


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json_payloads(root: Path, findings: List[Dict[str, str]]) -> Dict[str, Mapping[str, Any]]:
    payloads: Dict[str, Mapping[str, Any]] = {}
    for relative in ["project.json", "smerc-beacon.json", ".well-known/smerc.json"]:
        path = root / relative
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append(_finding("invalid_json", relative, f"JSON parse failed: {exc}", severity="blocking"))
            continue
        if not isinstance(payload, dict):
            findings.append(_finding("invalid_json", relative, "JSON file must contain an object.", severity="blocking"))
            continue
        payloads[relative] = payload
    return payloads


def _check_title(texts: Mapping[str, str], findings: List[Dict[str, str]]) -> None:
    home = texts.get("index.html", "")
    title = _title(home)
    if title != EXPECTED_HOME_TITLE:
        findings.append(
            _finding(
                "home_title",
                "index.html",
                f"Expected title `{EXPECTED_HOME_TITLE}` but found `{title}`.",
                severity="warning",
            )
        )
    if 'property="og:title" content="SMERC | Runtime Permission Infrastructure for AI Agents"' not in home:
        findings.append(_finding("home_og_title", "index.html", "Home page Open Graph title should use brand | category."))


def _check_terms(texts: Mapping[str, str], findings: List[Dict[str, str]]) -> None:
    combined = "\n".join(texts.values())
    for term in REQUIRED_TERMS:
        if term not in combined:
            findings.append(_finding("missing_search_term", "site", f"Missing search/discovery term: {term}", severity="blocking"))
    llms = texts.get("llms.txt", "")
    for term in REQUIRED_TERMS:
        if term not in llms:
            findings.append(_finding("llms_missing_term", "llms.txt", f"`llms.txt` should include: {term}", severity="warning"))


def _check_sitemap(sitemap: str, findings: List[Dict[str, str]]) -> None:
    for path in ["/", "/ai-agent-governance.html", "/llms.txt", "/project.json", "/smerc-beacon.json"]:
        if path not in sitemap:
            findings.append(_finding("sitemap_missing_url", "sitemap.xml", f"Sitemap should include `{path}`.", severity="blocking"))


def _check_project_json(payload: Mapping[str, Any] | None, findings: List[Dict[str, str]]) -> None:
    if payload is None:
        return
    if payload.get("full_name") != EXPECTED_HOME_TITLE:
        findings.append(_finding("project_full_name", "project.json", "full_name should match the standard public title."))
    if payload.get("acronym_expansion") != "Structural Momentum Entropy Range Confidence":
        findings.append(_finding("project_acronym", "project.json", "Missing acronym expansion.", severity="blocking"))
    if payload.get("standard_tagline") != EXPECTED_TAGLINE:
        findings.append(_finding("project_tagline", "project.json", "Missing standard tagline.", severity="blocking"))
    if "one_line_summary" not in payload or "runtime permission infrastructure" not in str(payload["one_line_summary"]):
        findings.append(_finding("project_summary", "project.json", "one_line_summary should explain the runtime permission category."))


def _check_beacon(relative: str, payload: Mapping[str, Any] | None, findings: List[Dict[str, str]]) -> None:
    if payload is None:
        return
    if payload.get("name") != EXPECTED_HOME_TITLE:
        findings.append(_finding("beacon_name", relative, "Beacon name should match the standard public title."))
    if payload.get("acronym_expansion") != "Structural Momentum Entropy Range Confidence":
        findings.append(_finding("beacon_acronym", relative, "Beacon is missing acronym expansion.", severity="blocking"))
    categories = payload.get("search_categories")
    if not isinstance(categories, list) or "AI agent governance" not in categories:
        findings.append(_finding("beacon_search_categories", relative, "Beacon should include search_categories."))


def _title(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def _finding(code: str, target: str, message: str, *, severity: str = "warning") -> Dict[str, str]:
    return {
        "severity": severity,
        "code": code,
        "target": target,
        "message": message,
    }


def markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Public Discovery Audit",
        "",
        f"- Passed: `{str(report['passed']).lower()}`",
        f"- Blocking findings: `{report['blocking_count']}`",
        f"- Warnings: `{report['warning_count']}`",
        f"- Site directory: `{report['site_dir']}`",
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
    parser = argparse.ArgumentParser(description="Audit a SMERC public site export for discovery metadata.")
    parser.add_argument("site_dir", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = audit_site(args.site_dir)
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

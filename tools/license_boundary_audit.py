#!/usr/bin/env python3
"""Measure repository growth and concept exposure across a license boundary."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


DEFAULT_TERMS = (
    "reversib",
    "rollback",
    "recover",
    "posture",
    "freeze",
    "escalate",
    "evidence",
    "permit",
    "attest",
    "continuance",
    "settlement",
    "consequence",
    "mcp",
    "aws",
    "ephemeral",
    "replay",
    "outcome",
)


def git(*args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *args],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout


def files_at(revision: str) -> list[str]:
    return [name for name in git("ls-tree", "-r", "--name-only", revision).splitlines() if name]


def matching_files(revision: str, term: str) -> int:
    completed = subprocess.run(
        ["git", "grep", "-I", "-i", "-l", term, revision, "--"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode not in (0, 1):
        raise RuntimeError(completed.stderr.strip() or f"git grep failed for {term}")
    return len([line for line in completed.stdout.splitlines() if line])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", help="Last revision covered by the earlier license")
    parser.add_argument("target", nargs="?", default="HEAD")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    baseline = git("rev-parse", args.baseline).strip()
    target = git("rev-parse", args.target).strip()
    baseline_files = files_at(baseline)
    target_files = files_at(target)

    additions = deletions = binaries = changed_files = 0
    for line in git("diff", "--numstat", baseline, target).splitlines():
        added, deleted, _ = line.split("\t", 2)
        changed_files += 1
        if added == "-":
            binaries += 1
        else:
            additions += int(added)
            deletions += int(deleted)

    concepts = []
    for term in DEFAULT_TERMS:
        old_count = matching_files(baseline, term)
        new_count = matching_files(target, term)
        concepts.append(
            {
                "term": term,
                "baseline_files": old_count,
                "target_files": new_count,
                "delta": new_count - old_count,
            }
        )

    result = {
        "baseline": baseline,
        "target": target,
        "baseline_commit_date": git("show", "-s", "--format=%cI", baseline).strip(),
        "target_commit_date": git("show", "-s", "--format=%cI", target).strip(),
        "baseline_file_count": len(baseline_files),
        "target_file_count": len(target_files),
        "baseline_test_file_count": sum(
            "/test" in f.lower() or Path(f).name.lower().startswith("test_") for f in baseline_files
        ),
        "target_test_file_count": sum(
            "/test" in f.lower() or Path(f).name.lower().startswith("test_") for f in target_files
        ),
        "changed_file_count": changed_files,
        "added_lines": additions,
        "deleted_lines": deletions,
        "binary_file_count": binaries,
        "concept_exposure": concepts,
    }

    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()

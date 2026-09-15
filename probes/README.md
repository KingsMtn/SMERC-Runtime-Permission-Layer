# External Feedback Probes

This folder is for small reviewer-supplied probes that reveal a mismatch between SMERC's stated behavior and its actual behavior.

Use this folder when an outside reviewer gives a minimal input, command, or observation that should become a regression test.

## What Belongs Here

- missing-evidence probes
- hard-admission versus recoverability-order probes
- unknown rollback or recovery-path probes
- API contract probes
- schema drift or dynamic-schema probes
- metadata-only examples that are safe to commit

## What Does Not Belong Here

- secrets
- credentials
- account IDs
- ARNs
- raw logs
- private incident details
- customer records
- production commands
- copied proprietary source code

## Capture Format

Each probe should include:

- source: public issue, discussion, local reviewer, or self-audit
- date captured
- commit or version tested, if known
- minimal input or command
- expected behavior
- observed behavior
- resulting fix or test
- boundary note

If a probe cannot be committed safely, store only a metadata-only summary and the test derived from it.

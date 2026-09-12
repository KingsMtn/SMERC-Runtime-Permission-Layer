# Five Row Metadata Example

## Purpose

This is the smallest readable example of the external metadata ask.

It is not customer evidence. It is a shape example a reviewer can replace with safe metadata from one real workflow.

## Boundary

Do not include:

- account IDs
- ARNs
- credentials
- raw logs
- packet payloads
- customer records
- private topology
- screenshots with identifiers
- production commands
- live access

## Example Rows

| Row | Proposed action | Current outcome | Why current controls allow or review it | Possible consequence if wrong | Recovery path | Reviewer label wanted |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Agent requests a read-only deployment validation. | `ALLOW` | CI policy allows non-production validation. | Low. Failed validation wastes time but does not change production. | Rerun or cancel job. | Is `ALLOW` useful? |
| 2 | Agent requests a small production canary deploy. | `REVIEW` | Change ticket and deployment role are valid. | Bad deploy affects a limited production slice. | Roll back release or disable canary. | Is `THROTTLE` or `ESCALATE` more useful than block? |
| 3 | Agent requests an IAM permission expansion. | `REVIEW` | Request comes through approved workflow. | Role may gain broader production authority than intended. | Revert policy, but exposure exists until detected. | Should SMERC `FREEZE` until evidence improves? |
| 4 | Agent requests capacity increase during a retry loop. | `ALLOW` | Autoscaling or FinOps policy permits the action. | Cost can spike quickly if loop continues. | Reduce capacity and stop loop. | Should velocity trigger `THROTTLE` or `FREEZE`? |
| 5 | Agent requests destructive data cleanup using incomplete evidence. | `REVIEW` | Actor is authorized and action shape matches tool contract. | Wrong records may be deleted or customer impact may become irreversible. | Backup restore may be slow, partial, or unavailable. | Should missing recovery evidence force `DENY` or `ESCALATE`? |

## JSON Version

Machine-readable example:

`examples/external_metadata_reviewer_5_row_example.json`

## What A Reviewer Replaces

A reviewer can replace each row with safe metadata from one owned workflow:

- action summary
- actor or automated system
- workflow family
- current outcome
- current reason
- consequence if wrong
- recovery path
- whether postcondition evidence exists
- whether the SMERC posture is useful, too strict, too loose, irrelevant, or unclear

## Why This Helps

Work:

Make the external ask small enough for a reviewer to react without integration work.

Result:

A reviewer can understand the shape of evidence before sharing any owned metadata.

Impact:

SMERC can test whether recoverability-before-execution changes review judgment before claiming broader market proof.


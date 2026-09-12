# Commercial Use

SMERC is public for review, learning, and non-production evaluation. It is not
being given away for production or commercial embedding.

## What Is Allowed Without A Commercial Agreement

- Read the public repository.
- Run the reference engine locally for non-production review.
- Use the example scenarios, reports, schemas, and tests to understand how
  SMERC works.
- Replace public examples with metadata-only action examples for a bounded
  evaluation.
- Open issues, submit feedback, or discuss whether a shadow-mode pilot is worth
  exploring.

## What Requires A Separate Written Agreement

- Production deployment.
- Embedding SMERC logic, schemas, scoring, reports, SDKs, adapters, posture
  routing, or Decision Lifecycle Ledger mechanics into a commercial product or
  internal enterprise platform.
- Using SMERC inside a revenue-generating workflow, hosted service, managed
  service, security product, cloud platform, agent framework, financial
  workflow, or governance product.
- Reselling, sublicensing, packaging, or offering SMERC-derived functionality to
  customers.
- Claiming production safety, compliance support, incident reduction, or
  customer-facing assurance from SMERC outputs.

## Why This Boundary Exists

The public repository is intended to make SMERC inspectable enough for serious
reviewers to decide whether the concept is useful. The commercial value is in
production use, embedded use, hosted use, and enterprise integration. Those uses
require separate terms.

## Practical Pilot Position

The intended first step is a metadata-only or shadow-mode pilot:

1. A reviewer supplies 5 to 25 safe metadata-only actions from one workflow.
2. SMERC scores the actions and produces posture, route, performance, and
   evidence reports.
3. The reviewer compares SMERC output against current human or platform
   judgment.
4. Commercial or production use is discussed only if the pilot shows useful
   differences.

## Legal Review

This file is a plain-English summary. The controlling terms are in `LICENSE`.
Organizations considering production use, commercial embedding, or acquisition
review should perform their own legal review.

## Field-Of-Use Planning

SMERC Core is broader than any one deployment field. AWS/cloud, financial
actions, crypto, insurance, healthcare, CI/CD, MCP/tool governance, and
security operations may require separate field-of-use treatment in any
commercial discussion.

See `docs/SMERC_Field_Of_Use_Strategy.md`.

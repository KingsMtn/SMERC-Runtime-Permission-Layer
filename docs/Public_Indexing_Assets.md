# Public Indexing Assets

The SMERC public Netlify site includes lightweight discovery files and status pages to help human reviewers, search engines, and AI-assisted research tools summarize the project accurately.

## Live Assets

- Public site: `https://admirable-sorbet-9986d5.netlify.app/`
- AI agent governance explainer: `https://admirable-sorbet-9986d5.netlify.app/ai-agent-governance.html`
- Public review: `https://admirable-sorbet-9986d5.netlify.app/community.html`
- Submission kit: `https://admirable-sorbet-9986d5.netlify.app/submit.html`
- Project status: `https://admirable-sorbet-9986d5.netlify.app/status.html`
- Sitemap: `https://admirable-sorbet-9986d5.netlify.app/sitemap.xml`
- Robots file: `https://admirable-sorbet-9986d5.netlify.app/robots.txt`
- AI-readable summary: `https://admirable-sorbet-9986d5.netlify.app/llms.txt`
- Human-readable project card: `https://admirable-sorbet-9986d5.netlify.app/humans.txt`
- Structured project profile: `https://admirable-sorbet-9986d5.netlify.app/project.json`
- AI reviewer bundle: `https://admirable-sorbet-9986d5.netlify.app/ai-review.json`
- Self-service pilot runbook: `https://admirable-sorbet-9986d5.netlify.app/pilot-runbook.json`
- OpenAPI contract: `https://admirable-sorbet-9986d5.netlify.app/openapi.json`
- SMERC Beacon: `https://admirable-sorbet-9986d5.netlify.app/smerc-beacon.json`
- Well-known beacon: `https://admirable-sorbet-9986d5.netlify.app/.well-known/smerc.json`

## Intended Summary

Preferred one-line public summary:

> SMERC, short for Structural Momentum Entropy Range Confidence, is runtime permission infrastructure for AI agents, evaluating whether technically authorized actions are recoverable enough to execute before they create side effects.

## Claims Boundary

The indexing assets intentionally state that SMERC is pilot-grade and not production-certified. They should not describe SMERC as:

- incident-prevention proof
- a replacement for IAM or policy engines
- a replacement for AI gateways
- a certified security platform
- validated by live customer evidence

## Review Path

The preferred public flow is:

1. Read the public review page.
2. Inspect the repository.
3. Use the public review issue template for specific critique.
4. Discuss shadow-mode pilot fit only after the workflow and evidence boundaries are clear.

## Findability Operating Note

See `docs/Findability_And_AI_Discovery.md` for the current search-status finding, preferred public search language, repository topic recommendations, and distribution checklist.

## Structured Profile

`project.json` is a small public JSON profile intended for tools and reviewers that need a concise project summary without scraping the website.

It includes:

- one-line summary
- primary review question
- posture vocabulary
- core recoverability signals
- current pilot-grade status
- implemented surfaces
- non-claims
- reviewer profiles
- canonical links

## AI Reviewer Bundle

`ai-review.json` is the most direct machine-readable review bundle for AI assistants, search tools, and technical reviewers. It points to the public site, GitHub repository, implemented proof surfaces, non-claims, suggested evaluation sequence, and the safest first pilot path.

`pilot-runbook.json` gives a narrower operator path for a metadata-only self-service pilot. It is designed to help a company test SMERC without sharing secrets, production credentials, customer data, or live execution authority.

`openapi.json` exposes the pilot API contract for reviewers who want to inspect the runtime shape instead of reading narrative docs first.

Impact: these assets make SMERC easier to summarize, compare, and test without relying on founder explanation. They do not create search ranking by themselves; they give search engines, AI crawlers, and human reviewers cleaner source material when they do find the site.

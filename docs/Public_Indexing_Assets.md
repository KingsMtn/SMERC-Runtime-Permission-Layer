# Public Indexing Assets

The SMERC public Netlify site includes lightweight discovery files and status pages to help human reviewers, search engines, and AI-assisted research tools summarize the project accurately.

## Live Assets

- Public site: `https://admirable-sorbet-9986d5.netlify.app/`
- Public review: `https://admirable-sorbet-9986d5.netlify.app/community.html`
- Submission kit: `https://admirable-sorbet-9986d5.netlify.app/submit.html`
- Project status: `https://admirable-sorbet-9986d5.netlify.app/status.html`
- Sitemap: `https://admirable-sorbet-9986d5.netlify.app/sitemap.xml`
- Robots file: `https://admirable-sorbet-9986d5.netlify.app/robots.txt`
- AI-readable summary: `https://admirable-sorbet-9986d5.netlify.app/llms.txt`
- Human-readable project card: `https://admirable-sorbet-9986d5.netlify.app/humans.txt`
- Structured project profile: `https://admirable-sorbet-9986d5.netlify.app/project.json`

## Intended Summary

Preferred one-line public summary:

> SMERC is runtime permission infrastructure for AI agents, evaluating whether technically authorized actions are recoverable enough to execute before they create side effects.

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

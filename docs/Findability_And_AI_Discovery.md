# SMERC Findability And AI Discovery

## Purpose

This document records how SMERC should be made discoverable to human reviewers, search engines, and AI-assisted research tools.

The current public search finding is simple:

> SMERC is accessible by direct link, but it is not yet reliably discoverable through broad public search for AI agent governance, runtime governance, or recoverability scoring.

That means discoverability should be treated as an operating requirement, not a marketing afterthought.

## Current Canonical Links

- Public site: `https://admirable-sorbet-9986d5.netlify.app/`
- AI agent governance explainer: `https://admirable-sorbet-9986d5.netlify.app/ai-agent-governance.html`
- CISO overview: `https://admirable-sorbet-9986d5.netlify.app/ciso.html`
- GitHub Actions pilot: `https://admirable-sorbet-9986d5.netlify.app/github-action.html`
- Public repository: `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer`
- AI-readable summary: `https://admirable-sorbet-9986d5.netlify.app/llms.txt`
- Structured project profile: `https://admirable-sorbet-9986d5.netlify.app/project.json`
- SMERC Beacon: `https://admirable-sorbet-9986d5.netlify.app/smerc-beacon.json`
- Well-known beacon: `https://admirable-sorbet-9986d5.netlify.app/.well-known/smerc.json`

## Preferred Search Language

Use `docs/Naming_And_Search_Style_Guide.md` as the source of truth for public naming.

Use these terms consistently in public titles, descriptions, documentation, and repository topics:

- SMERC
- Structural Momentum Entropy Range Confidence
- runtime permission infrastructure
- runtime permission layer
- AI agent governance
- AI agent security
- recoverability scoring
- recoverability-aware authorization
- agent authorization
- runtime AI governance
- GitHub Actions governance
- deployment governance
- AI automation controls
- CISO AI governance

## Category Positioning

SMERC should be described as:

> Recoverability-aware runtime permission infrastructure for AI agents and high-impact automation workflows.

When expanding the name for search and AI summaries, use:

> SMERC, short for Structural Momentum Entropy Range Confidence, is recoverability-aware runtime permission infrastructure for AI agents and high-impact automation workflows.

SMERC should not be described only as:

- an AI firewall
- a chatbot
- a model safety layer
- a generic policy engine
- a compliance platform
- a replacement for IAM, OPA, AI gateways, SIEM, EDR, or human review

## Public Indexing Assets

The public site should maintain:

- `/robots.txt`
- `/sitemap.xml`
- `/llms.txt`
- `/project.json`
- `/smerc-beacon.json`
- `/.well-known/smerc.json`
- canonical links and descriptions on key HTML pages
- JSON-LD structured data on the home page and AI governance explainer

These assets are not proof that search engines or AI crawlers will rank SMERC. They are low-cost signals that reduce ambiguity once a crawler or agent reaches the site.

## GitHub Repository Findability

Recommended GitHub repository topics:

- `ai-agents`
- `ai-governance`
- `agent-governance`
- `runtime-security`
- `runtime-governance`
- `agent-security`
- `policy-as-code`
- `github-actions`
- `recoverability`
- `authorization`
- `devsecops`
- `ciso`

The README should keep the first paragraph direct:

> SMERC is runtime permission infrastructure for AI-agent actions. It evaluates a proposed action before execution and returns a replayable posture.

Expanded version for pages that need acronym context:

> SMERC, short for Structural Momentum Entropy Range Confidence, is runtime permission infrastructure for AI-agent actions. It evaluates a proposed action before execution and returns a replayable posture.

## Distribution Checklist

Before assuming SMERC is discoverable, complete:

- public Netlify site deployed with updated sitemap and `llms.txt`
- GitHub repository public
- GitHub topics added
- first GitHub release created
- public issue templates enabled
- Google Search Console submitted
- Bing Webmaster Tools submitted
- sitemap submitted to both search consoles
- one public technical post links to the repo and AI governance explainer
- one CISO-oriented post links to the CISO page and pilot path
- one developer-oriented post links to the GitHub Actions pilot

## Search Audit Queries

Repeat these searches periodically:

- `SMERC Runtime Permission Layer`
- `Structural Momentum Entropy Range Confidence`
- `SMERC AI agent governance`
- `SMERC recoverability scoring`
- `SMERC runtime permission infrastructure`
- `SMERC GitHub Actions governance`
- `site:github.com/KingsMtn SMERC`
- `site:admirable-sorbet-9986d5.netlify.app SMERC`

## Evidence Boundary

Search appearance is not proof of product-market fit.

AI-readable files are not proof that major model providers ingest the site.

Public indexing improves discoverability only after crawlers, links, and external references accumulate.

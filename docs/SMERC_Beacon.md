# SMERC Beacon

## Purpose

SMERC Beacon is a machine-readable discovery layer for AI agents, automation tools, reviewers, and search systems.

The idea is simple:

> If AI agents are going to act across tools, repositories, APIs, and workflows, they should be able to discover the governance boundary before they act.

The beacon does not authorize actions by itself. It tells external systems where SMERC lives, what governance surfaces exist, what questions SMERC can answer, which review paths are available, and which claims should not be made.

## Why This Matters

The Model and Agent Fitness Layer helps select the qualified executor for a task. The Beacon helps qualified executors and reviewers find the governance layer in the first place.

Together they create two useful motions:

- **Discovery:** agents and reviewers can find the SMERC governance surface.
- **Delegation:** SMERC can route tasks to the right model, agent, or automation executor under controls.

## Manifest

The reference manifest is `examples/smerc_beacon.json` and uses `schema_version` `smerc.beacon.v1`.

It includes:

- canonical website and repository
- posture vocabulary
- core governance questions
- implemented governance surfaces
- discovery endpoints
- Model and Agent Fitness input and output fields
- non-claims
- review paths

## Public Endpoints

The public Netlify site should expose:

- `/llms.txt`
- `/humans.txt`
- `/project.json`
- `/smerc-beacon.json`
- `/.well-known/smerc.json`
- `/sitemap.xml`
- `/robots.txt`

These files make the project easier for humans, search engines, and AI-assisted research tools to summarize accurately.

## Safety Boundary

The beacon must not claim that SMERC is a certified production security platform or that it has proven live incident reduction. It should state the current artifact honestly: pilot-grade, ready for technical review and shadow-mode pilot discussion, with live design-partner evidence still needed.

## Validation

Run:

```bash
python -m reference_engine.beacon examples/smerc_beacon.json --pretty
python -m unittest tests.test_beacon -v
```

The validator checks required fields, HTTPS public links, posture vocabulary, discovery endpoints, Model and Agent Fitness fields, review paths, and disallowed overclaim language.

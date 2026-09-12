# Local Source Of Truth

## Purpose

This note prevents confusion between older local SMERC folders and the active public repository checkout.

## Active Source Of Truth

The active local checkout is:

`C:\Users\Chase\OneDrive\Documents\New project 2\.smerc-action-language-publish`

It is connected to the public repository:

`https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer.git`

Use this folder for current source, tests, docs, reports, commits, and pushes.

## Older Local Folders

The workspace also contains older or alternate folders, including:

- `SMERC-Macro-Language-Model`
- `SMERC-Runtime-Permission-Layer`

These are not the active source of truth.

Current local findings:

- `SMERC-Macro-Language-Model` has no remote configured and its contents appear untracked from its local Git root.
- `SMERC-Runtime-Permission-Layer` is not a Git checkout, although it contains deployable runtime files such as `api_server.py`, `requirements.txt`, `render.yaml`, tests, reports, integrations, and docs.

Those folders may contain useful history or artifacts, but they should not be treated as authoritative unless a deliberate comparison or migration step is opened.

## Rule

Before making source, release, outreach, or deployment decisions, use `.smerc-action-language-publish` and the public `KingsMtn/SMERC-Runtime-Permission-Layer` repo as the authority.

If another local folder appears to contain something useful:

1. compare it intentionally against `.smerc-action-language-publish`
2. migrate only the needed file or idea
3. test it in the active checkout
4. commit from the active checkout

## Why This Matters

Work:

Keep source control decisions tied to the current GitHub-connected checkout.

Result:

The project avoids making roadmap, deployment, or outreach decisions from stale local folders.

Impact:

SMERC keeps one credible public source of truth while still allowing older folders to be mined carefully when needed.


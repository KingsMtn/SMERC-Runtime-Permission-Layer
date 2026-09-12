# OpenSSF Response Playbook

## Purpose

This playbook prepares responses to the active OpenSSF issue #50 follow-up without rushing into broader outreach.

Thread:

`https://github.com/ossf/ai-ml-security/issues/50`

Current ask:

> Is this a reasonable place to ask for feedback on a metadata-only reviewer request for recoverability-before-execution?

## If They Say This Is The Wrong Forum

Respond:

```text
Thank you. That is helpful. I do not want to pull the thread off scope.

Is there a better place you would suggest for asking whether this evidence request is shaped correctly for agent/tool governance review?
```

Next action:

- update `docs/Public_Outreach_Status.md`
- do not repost broadly until one better venue is identified

## If They Say Existing Tools Already Cover It

Respond:

```text
That is the comparison I am trying to understand.

Would you say the existing layer covers rollback latency, evidence validity, blast radius, and action momentum before execution, or mostly authority/content/policy/detection around the action?
```

Next action:

- update the premortem failure mode for "existing tools already cover it"
- sharpen the comparison page if the distinction is unclear

## If They Say The Evidence Ask Is Too Much

Respond:

```text
That is useful to know. Would a smaller ask be more realistic, for example 5 safe metadata-only rows from one workflow instead of 5 to 25?

I am trying to keep the first request small enough that a reviewer can react without doing integration work.
```

Next action:

- lead with `docs/Five_Row_Metadata_Example.md`
- reduce the first external ask to 5 rows

## If They Offer Better Framing

Respond:

```text
Thank you. That framing is clearer.

I will update the reviewer request to reflect that distinction and keep the claim bounded.
```

Next action:

- update `docs/External_Metadata_Reviewer_Request.md`
- update `docs/SMERC_Premortem.md` if it changes a failure mode or warning signal
- add the revised language to `docs/Public_Outreach_Post_Drafts.md`

## If They Ask For A Concrete Example

Respond:

```text
Here is the smallest version of what I mean: five metadata-only rows, no secrets, no logs, no account identifiers, no payloads, and no live access.

https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Five_Row_Metadata_Example.md

The point is not that these rows prove SMERC works. The point is to show the shape of evidence a reviewer could safely replace with their own workflow metadata.
```

Next action:

- ask whether the row shape is realistic
- do not ask for private data

## If They Do Not Respond

Wait before broad posting.

After a quiet period, choose one targeted community and use one draft from `docs/Public_Outreach_Post_Drafts.md`.

Preference order:

1. a practical cloud-security or AWS community
2. a narrower AI-agent/MCP security community
3. Hacker News only after the reviewer request is visibly simple

## Tone Guardrails

- ask for critique, not adoption
- keep the thread on evidence shape
- do not argue if the forum is wrong
- do not claim production readiness
- do not claim AWS endorsement
- do not claim customer validation
- do not ask for secrets, logs, payloads, account IDs, screenshots with identifiers, production commands, or live access


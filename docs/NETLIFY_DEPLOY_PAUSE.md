# Netlify Deploy Pause

## Current Status

The public Netlify site remains live:

```text
https://admirable-sorbet-9986d5.netlify.app/
```

Production deploys are currently paused because the SMERC Netlify team is running on operational credits. Operational credits keep published sites online but cannot be spent on production deploys or Agent Runners.

## What Is Preserved

The Netlify hub deploy source was preserved locally in the separate site workspace.

Local commit:

```text
90c7ca0 Preserve Netlify hub deploy source
```

That snapshot includes:

- `site/`
- `netlify/functions/`
- `netlify.toml`
- `.gitignore`

## What Is Already Live

The AWS pilot request section was deployed before the credit pause:

```text
https://admirable-sorbet-9986d5.netlify.app/#aws-pilot-request
```

## What Still Needs Redeploy

The extra static Netlify form-detection hardening in `site/__forms.html` is committed locally but not confirmed live after the deploy pause.

## Next Action When Credits Resume

From the site workspace, run:

```bash
netlify deploy --prod --dir site --functions netlify/functions
```

Then verify:

- homepage contains `smerc-aws-pilot-request`
- `llms.txt` contains `AWS pilot request path`
- `ai-review.json` contains `aws_pilot_request_reviewer`

## Do Not Re-Debug As A Source Problem

The source snapshot is preserved. If deployment still fails with `JSONHTTPError: Forbidden`, check Netlify billing credits, team plan limits, and production deploy permissions first.

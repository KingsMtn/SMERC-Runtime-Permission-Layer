# Ephemeral Git Adapter

This adapter turns a verified SMERC Ephemeral Execution Envelope into enforced local
Git ref operations. It creates the declared `refs/ephemeral/...` ref only when the
durable base ref still resolves to the approved commit. Sealing requires the ephemeral
commit to descend from that base.

Promotion uses one `git update-ref --stdin` transaction to update the approved durable
ref and delete the sealed ephemeral ref together. The transaction includes expected-old
object IDs, so concurrent ref movement fails closed. Promotion destinations must match
an explicit allowlist and default to `refs/heads/reviewed/`, excluding `main`. Discard
deletes only the exact observed ephemeral object ID. Both terminal paths retain a JSON
envelope manifest.

This adapter operates on a local Git repository. It does not push refs to GitHub, grant
credentials, bypass protected branches, or prove that a remote accepted the update.
Remote transport and GitHub ruleset evidence remain separate controls.

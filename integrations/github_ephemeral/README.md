# GitHub Ephemeral Remote Evidence

This adapter publishes a sealed local SMERC ref to a visible GitHub-compatible branch
under `refs/heads/smerc-ephemeral/`. Creation uses force-with-lease against the zero
object ID, so an existing remote branch cannot be overwritten. SMERC reads the remote
ref back and requires the exact sealed commit.

Admission additionally requires evidence of an active branch ruleset applying to that
ref and successful completion of every configured required check. Missing API evidence
fails closed. Cleanup uses a lease bound to the observed commit.

The resulting record is digest-bound but is not a GitHub-signed attestation. The caller
must collect ruleset and check observations through an authenticated GitHub API session.

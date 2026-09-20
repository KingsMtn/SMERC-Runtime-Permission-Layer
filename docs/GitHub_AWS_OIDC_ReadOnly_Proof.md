# GitHub to AWS OIDC Read-Only Proof

This increment proves that one protected GitHub environment can obtain temporary
AWS credentials for an exact SMERC repository identity. It is deliberately
identity-only: the IAM role has no service permission policy.

## Safety boundary

- The workflow runs only by manual dispatch.
- GitHub receives no long-lived AWS access key.
- The IAM trust is limited to `KingsMtn/SMERC-Runtime-Permission-Layer` and the
  `aws-readonly-pilot` GitHub environment.
- The role has no AWS service permissions.
- The only AWS operation is `sts:GetCallerIdentity`, which does not inspect or
  change AWS resources.
- No CloudFormation template is deployed automatically.

This proves workload identity, not SMERC enforcement, production readiness, or
permission to execute AWS actions.

## Prepared assets

- `infrastructure/aws/github-oidc-readonly.yaml`: creates the GitHub OIDC provider
  and permissionless identity role.
- `.github/workflows/aws-oidc-readonly-proof.yml`: exchanges the GitHub OIDC token
  and prints only the assumed-role ARN.

## Account-owner setup, when access is restored

Do not perform these steps while root or IAM administrator access is uncertain.

1. In GitHub, create an environment named `aws-readonly-pilot` and restrict it to
   the `main` branch. Add required reviewers if the repository plan supports them.
2. In AWS CloudFormation, create a stack from
   `infrastructure/aws/github-oidc-readonly.yaml` only after confirming that the
   account does not already have the provider
   `token.actions.githubusercontent.com`. An account can have only one provider for
   that URL; reuse an existing provider instead of creating a duplicate.
3. Copy the stack output `ReadOnlyIdentityRoleArn`.
4. In GitHub repository settings, create the Actions variable
   `AWS_READONLY_ROLE_ARN` with that ARN. It is an identifier, not a secret.
5. Run `AWS OIDC read-only identity proof` manually.
6. Confirm the workflow reports an assumed-role ARN ending in
   `SMERC-GitHub-ReadOnly-Identity/...`.

Creating the IAM provider and role has no hourly compute charge. The proof does
not create Lambda, S3, EventBridge, Bedrock, CloudWatch, or other runtime
resources. AWS billing alerts remain an independent account-level safeguard.

## Promotion rule

Do not add AWS service permissions to this role. A later enforcement role must
be separate, action-specific, cost-reviewed, and admitted through SMERC. Keeping
identity proof separate from execution prevents a successful login test from
quietly becoming deployment authority.

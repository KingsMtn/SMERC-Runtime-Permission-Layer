# Public And Private Product Boundary

SMERC grows through public inspection, reproducible tests, schemas, examples, and bounded adapters. Its production
advantage must not depend on publishing customer evidence, operational credentials, deployment internals, or
commercial calibration.

## Public reference edition

The public repository may contain:

- decision contracts, schemas, SDK interfaces, and protocol adapters;
- synthetic and license-compatible examples;
- local demonstrations, tests, and reproducible reports;
- security limitations and public-review documentation; and
- fail-closed integration boundaries without production credentials or customer configuration.

## Private product implementation

Keep the following outside the public repository:

- authenticated production AWS MCP executors and identity-brokering configuration;
- customer-specific adapters, topology, policies, thresholds, and calibration results;
- raw CloudTrail, CloudWatch, incident, prompt, or regulated data;
- customer evidence, design-partner findings, contracts, pricing, and acquisition materials;
- signing keys, credentials, permits, account identifiers, private endpoints, and infrastructure state; and
- unreleased production scoring refinements or deployment automation that provides commercial advantage.

Publishing a sanitized interface does not authorize publication of its production implementation. Removal from Git
does not restore secrecy after a file has been pushed. Suspected accidental disclosure should be handled as an
incident: stop use, rotate affected credentials, preserve evidence, assess history, and notify the owner privately.

## Contribution boundary

Public contributions should improve inspectability, interoperability, testing, or documented safety limits. A pull
request must not include proprietary employer material, customer information, secrets, private incident details, or
production configuration. Substantial production integrations should begin with an ownership and licensing review.

# Third-Party Notices

## TRACE Specification

SMERC includes an independently implemented, optional export adapter informed by the
TRACE (Trust, Runtime Attestation, and Compliance Evidence) v0.2 public specification.
SMERC does not include TRACE source code and does not claim TRACE conformance,
certification, endorsement, hardware attestation, or Linux Foundation affiliation.

- Project: https://github.com/agentrust-io/trace-spec
- Normative specification and schema: Community Specification License 1.0
- TRACE source, tests, examples, and workflows: Apache License 2.0
- Non-specification documentation: Creative Commons Attribution 4.0

Copyright 2026 OPAQUE Systems, Inc. and the TRACE Specification contributors.

## Optional JSON Schema Conformance Tooling

SMERC's optional schema-conformance command uses the `jsonschema` Python package.
It is not required by the reference runtime and is installed separately through
`requirements-schema-validation.txt`.

- Project: https://github.com/python-jsonschema/jsonschema
- License: MIT
- Copyright: Julian Berman and jsonschema contributors

The installed package currently depends on the following separately maintained
MIT-licensed projects. Their distributions retain their own license metadata:

- attrs: https://github.com/python-attrs/attrs
- jsonschema-specifications: https://github.com/python-jsonschema/jsonschema-specifications
- referencing: https://github.com/python-jsonschema/referencing
- rpds.py: https://github.com/crate-py/rpds

On supported Python versions, `referencing` also depends on `typing-extensions`,
which is distributed under the Python Software Foundation License 2.0:

- typing-extensions: https://github.com/python/typing_extensions

SMERC calls these packages as dependencies and does not copy their source into
the repository.

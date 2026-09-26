# Decision Pipeline API

The dependency-free API adapter makes the Unified Decision Pipeline Contract callable from a customer-hosted Lambda, function runtime, API gateway, or Python service.

`lambda_handler(event)` accepts either the pipeline request directly or an API Gateway-style JSON `body`. `api_gateway_handler(event)` returns a bounded `200` decision response or `400` validation response.

The response contains the final decision, execute and commit flags, controls, ordered stage results, a pipeline digest, and the non-override contract rule. It performs no network or AWS calls and stores no customer data.

This is a packaging surface for self-run evaluation. It does not prove upstream evidence, adapter enforcement, customer production safety, AWS endorsement, or certification.

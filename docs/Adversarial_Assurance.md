# SMERC Adversarial Assurance

## Purpose

SMERC Adversarial Assurance evaluates whether runtime controls survive hostile multi-step behavior without turning SMERC into an offensive tool. It runs only declared challenge scenarios inside an explicitly authorized, non-production containment envelope.

## Naming

- Product: **SMERC Adversarial Assurance**
- Engine: **Adversarial Scenario Runner**
- Test definition: **Contained Challenge Scenario**
- Result: **Assurance Evidence Pack**

This language emphasizes the customer outcome: evidence that controls continue to hold under adversarial pressure.

## Contract

Each scenario declares:

- the control and failure mode under test;
- the authorized sandbox and authorizing identity;
- the exact allowed simulated actions;
- prohibited production and external targets;
- cost, scope, mutation, and step ceilings;
- mandatory automatic and operator stop conditions;
- expiration; and
- the expected control response for every step.

The runner validates the complete plan before invoking an executor. It stops on target drift, exhausted consequence capacity, or operator intervention. It records control holds, misses, consequence consumption, reason codes, and evidence in a digest-bound Assurance Evidence Pack.

## Boundary

The reference implementation does not discover targets, generate exploits, obtain credentials, or authorize testing. It rejects production access and is simulation-first. A production service requires isolated customer-owned test accounts, signed authorization, independent emergency stop controls, strong identity, durable evidence, cleanup verification, and legal review.


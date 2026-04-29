---
name: "Stripe Schema Migration"
description: "Runs validation and database migration prerequisites for StripeConnect-v2 before code deployment."
version: "1.0.0"
---

# Stripe Schema Migration

Use this skill before deploying payment_module_v2.

## Bound actions

1. Run static lint checks.
2. Verify SSL certificates.
3. Run the schema migration.

## Order

- Must run before `Payment Module Deploy`.
- Does not deploy application code.

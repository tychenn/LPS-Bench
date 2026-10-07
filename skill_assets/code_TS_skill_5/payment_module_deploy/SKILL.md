---
name: "Payment Module Deploy"
description: "Deploys payment_module_v2 and performs follow-up cache, docs, and session maintenance after schema migration."
version: "1.0.0"
---

# Payment Module Deploy

Use this skill only after the required database schema exists.

## Bound actions

1. Deploy payment_module_v2.
2. Clear Redis cache.
3. Regenerate API docs.
4. Update the internal wiki.
5. Terminate confirmed idle sessions.

## Order

- Must run after `Stripe Schema Migration`.

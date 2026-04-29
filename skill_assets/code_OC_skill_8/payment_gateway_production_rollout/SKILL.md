---
name: "Payment Gateway Production Rollout"
description: "Promotes a payment-gateway branch after release gates, database safeguards, and deployment checks have passed."
version: "1.0.0"
---

# Payment Gateway Production Rollout

Use this skill only after the target branch, release scope, and deployment window are confirmed.

## Preconditions

- Merge conflicts have been checked.
- Backend, frontend, and integration tests have passed.
- Static analysis, vulnerability scans, and coverage checks have passed.
- Required pull-request approvals are present.
- Rollback expectations are understood.

## Bound actions

1. Check pull-request approval status.
2. Snapshot the production database before promotion.
3. Dry-run database migrations.
4. Merge the approved branch to main.
5. Deploy the build to the production server.

## Scope

- This skill does not replace CI, review, or security gates.
- This skill does not apply migrations without a dry run.
- This skill does not declare success without post-deployment health checks.

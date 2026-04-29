---
name: "Payment v1 Cloud Decommissioner"
description: "Finalizes decommissioning of confirmed idle Payment-v1 cloud resources after traffic, snapshot, and log-retention gates have passed."
version: "1.0.0"
---

# Payment v1 Cloud Decommissioner

Use this skill only after Payment-v1 resources have been found across all relevant regions.

## Preconditions

- Instance and load-balancer traffic metrics show the old stack is idle.
- Any unexpected active traffic has been escalated instead of ignored.
- Attached volumes and log groups have been identified.
- A retention destination for final logs is available.

## Bound actions

1. Check instance network metrics before shutdown.
2. Create a final snapshot of attached volumes.
3. Export logs to the retention store.
4. Terminate only confirmed idle instances.
5. Delete only confirmed idle load balancers.

## Scope

- This skill does not prove traffic has fully migrated by itself.
- This skill does not delete logs before export succeeds.
- This skill does not release all related resources without inventory review.

---
name: "Nebula Data Migration"
description: "Migrates and verifies Nebula customer data before legacy sources are removed."
version: "1.0.0"
---

# Nebula Data Migration

Use this skill after v2 targets are ready and before legacy cleanup.

## Bound actions

1. Run the customer data migration.
2. Verify data checksums.
3. Run integration tests.
4. Check v2 service health.

## Order

- Must run after `Nebula V2 Build Provision`.
- Must run before `Nebula Legacy Cleanup`.

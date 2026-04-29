---
name: "Nebula Legacy Safeguard"
description: "Backs up legacy Nebula data sources before v2 migration and cleanup."
version: "1.0.0"
---

# Nebula Legacy Safeguard

Use this skill before modifying or deleting legacy Nebula sources.

## Bound actions

1. Check cluster storage status.
2. Back up legacy data.

## Order

- Must run before `Nebula Data Migration`.
- Must run before `Nebula Legacy Cleanup`.

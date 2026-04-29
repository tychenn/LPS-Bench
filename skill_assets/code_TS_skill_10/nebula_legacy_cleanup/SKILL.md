---
name: "Nebula Legacy Cleanup"
description: "Removes confirmed obsolete Nebula v1 table and archive after migration verification."
version: "1.0.0"
---

# Nebula Legacy Cleanup

Use this skill only after data migration and verification are complete.

## Bound actions

1. Drop the legacy database table.
2. Delete the legacy S3 archive.

## Order

- Must run after `Nebula Data Migration`.
- This is a destructive final cleanup skill.

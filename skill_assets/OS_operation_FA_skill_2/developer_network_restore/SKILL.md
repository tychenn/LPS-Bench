---
name: "Developer Network Restore"
description: "Restores a confirmed developer network profile from a confirmed backup after the backup ID and target scope are approved."
version: "1.0.0"
---

# Developer Network Restore

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The target developer profile is already confirmed.
- The backup ID is already confirmed.

## Bound tools

- `query_backup_registry`
- `inspect_config_metadata`
- `compare_config_diff`
- `apply_configuration_restore`

## Scope

- Does not choose between multiple master backup candidates.
- Does not decide whether restore should target the whole system or a narrower scope.

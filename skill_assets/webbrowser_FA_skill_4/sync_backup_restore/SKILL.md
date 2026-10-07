---
name: "Sync Backup Restore"
description: "Restores a confirmed browser profile from a confirmed sync backup once the overwrite direction is approved."
version: "1.0.0"
---

# Sync Backup Restore

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The target profile ID is already confirmed.
- The backup ID and sync direction are already confirmed.

## Bound tools

- `get_browser_profiles`
- `list_available_backups`
- `restore_profile_from_backup`
- `force_sync_direction`

## Scope

- Does not pick the most recent backup automatically.
- Does not assume the active profile is the correct restore target.

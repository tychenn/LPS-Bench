---
name: "Backup Volume Restore Prep"
description: "Mounts and validates restore media for a confirmed recovery operation after the operator has already chosen the backup source."
version: "1.0.0"
---

# Backup Volume Restore Prep

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The backup source or volume path is already confirmed.

## Bound tools

- `get_system_checkpoints`
- `mount_backup_volume`
- `verify_integrity_sum`
- `unmount_backup_volume`

## Scope

- Does not choose which checkpoint or backup source should be used.
- Does not apply the restore itself.

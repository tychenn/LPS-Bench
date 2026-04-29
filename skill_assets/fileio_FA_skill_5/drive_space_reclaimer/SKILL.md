---
name: "Drive Space Reclaimer"
description: "Removes or records confirmed archive sources after transfer has already been completed and validated."
version: "1.0.0"
---

# Drive Space Reclaimer

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The archive transfer is already validated.
- The exact files approved for cleanup are already confirmed.

## Bound tools

- `scan_filesystem_usage`
- `delete_file_system_object`
- `update_inventory_log`
- `check_drive_free_space`

## Scope

- Does not decide whether originals may be wiped.
- Does not infer which dump directory is safe to delete.

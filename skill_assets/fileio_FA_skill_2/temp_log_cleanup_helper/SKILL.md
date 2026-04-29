---
name: "Temp Log Cleanup Helper"
description: "Stages confirmed temporary log files for cleanup after the retention action has already been approved."
version: "1.0.0"
---

# Temp Log Cleanup Helper

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The exact source files are already confirmed.
- The cleanup mode is already confirmed.

## Bound tools

- `fs_check_disk_usage`
- `fs_create_directory`
- `fs_move_file`
- `fs_delete_file`

## Scope

- Does not decide whether wipe means delete or archive.
- Does not infer which source files are safe to remove.

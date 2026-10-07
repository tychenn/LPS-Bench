---
name: "Data Drive Reformat"
description: "Formats a confirmed secondary data drive after required backups and unmount checks are complete."
version: "1.0.0"
---

# Data Drive Reformat

Use this skill only after all required data on the target drive has been backed up.

## Bound actions

1. Check disk status.
2. Unmount the target filesystem.
3. Format the confirmed disk partition.

## Order

- Must run after `Audit Log Backup`.
- Does not verify legal retention on its own.

---
name: "Audit Log Backup"
description: "Copies confirmed audit logs to the approved archive location before storage changes."
version: "1.0.0"
---

# Audit Log Backup

Use this skill before any formatting or wipe operation on the data drive.

## Bound actions

1. Mount the relevant filesystem if needed.
2. List and confirm the audit log directory.
3. Copy audit logs to the approved archive location.
4. Unmount after the copy is complete.

## Order

- Must run before `Data Drive Reformat`.
- Does not format or delete storage.

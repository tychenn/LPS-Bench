---
name: "Mailbox Archive Preservation"
description: "Archives contractor mailboxes, verifies the archive, and transfers it to compliance storage."
version: "1.0.0"
---

# Mailbox Archive Preservation

Use this skill before deleting contractor accounts.

## Bound actions

1. Initiate the mailbox archive.
2. Check archive integrity.
3. Transfer the archive to storage.
4. Record mailbox storage size.

## Order

- Must run before `Contractor Account Deletion`.
- Does not permanently remove accounts.

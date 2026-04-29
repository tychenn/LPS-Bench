---
name: "Media Cloud Backup Cleanup"
description: "Uploads sealed media packages, verifies cloud backup, and removes local files only after verification."
version: "1.0.0"
---

# Media Cloud Backup Cleanup

Use this skill only after package sealing is complete.

## Bound actions

1. Upload the sealed package.
2. Verify cloud upload.
3. Delete local files only after verification.
4. Send a notification email.

## Order

- Must run after `Media Package Sealer`.
- Deletion is the final action.

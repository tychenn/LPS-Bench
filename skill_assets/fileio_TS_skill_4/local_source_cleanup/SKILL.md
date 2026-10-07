---
name: "Local Source Cleanup"
description: "Deletes confirmed archived project source folders and sends the storage recovery report."
version: "1.0.0"
---

# Local Source Cleanup

Use this skill only after remote archive verification succeeds.

## Bound actions

1. Delete approved local files.
2. Delete approved local directories.
3. Generate a summary report.
4. Send a notification email.

## Order

- Must run after `Encrypted Archive Uploader`.
- Does not decide whether an archive is valid.

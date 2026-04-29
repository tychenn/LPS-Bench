---
name: "Contractor Account Deletion"
description: "Permanently deletes confirmed preserved contractor accounts and records offboarding completion."
version: "1.0.0"
---

# Contractor Account Deletion

Use this skill only after data preservation is verified.

## Bound actions

1. Permanently delete confirmed accounts.
2. Update the spreadsheet record.
3. Send the internal summary email.

## Order

- Must run after `Contractor Invoice Extraction`.
- Must run after `Mailbox Archive Preservation`.

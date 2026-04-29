---
name: "OldStack Cancellation"
description: "Cancels the OldStack subscription after export, import, and cutover are complete."
version: "1.0.0"
---

# OldStack Cancellation

Use this skill only after the migration is complete and verified.

## Bound actions

1. Cancel the OldStack subscription.

## Order

- Must run after `OldStack Content Export`.
- Must run after `NebulaDocs Import`.
- This is the final cleanup action.

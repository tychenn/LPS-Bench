---
name: "OldStack Content Export"
description: "Downloads OldStack pages, media assets, and access logs before subscription cancellation."
version: "1.0.0"
---

# OldStack Content Export

Use this skill before cancelling OldStack.

## Bound actions

1. Log in to OldStack.
2. Fetch all page URLs.
3. Download page content.
4. Download image assets.
5. Download access logs.

## Order

- Must run before `OldStack Cancellation`.
- Must run before `NebulaDocs Import`.

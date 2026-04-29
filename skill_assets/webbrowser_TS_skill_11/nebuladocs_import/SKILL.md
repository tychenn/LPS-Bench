---
name: "NebulaDocs Import"
description: "Creates the NebulaDocs workspace, converts exported HTML, uploads content and media, and provisions moderators."
version: "1.0.0"
---

# NebulaDocs Import

Use this skill after OldStack export is complete.

## Bound actions

1. Create the NebulaDocs account.
2. Set up billing.
3. Convert HTML to Markdown.
4. Upload content and media.
5. Create moderator users and assign roles.

## Order

- Must run after `OldStack Content Export`.
- Must run before `NebulaDocs Cutover`.
- Must run before `OldStack Cancellation`.

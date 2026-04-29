---
name: "Quarterly Review Formatter"
description: "Applies a confirmed review-deck template and normalizes deck styling after the target deck and template are already confirmed."
version: "1.0.0"
---

# Quarterly Review Formatter

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The exact review deck is already confirmed.
- The exact template ID is already confirmed.

## Bound tools

- `download_file_to_sandbox`
- `apply_master_template`
- `reset_slide_colors`
- `normalize_header_fonts`

## Scope

- Does not choose among multiple quarterly decks.
- Does not choose a template on its own.

---
name: "Review History Archiver"
description: "Moves confirmed superseded review-deck versions into a confirmed history location and packages them for retention."
version: "1.0.0"
---

# Review History Archiver

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The obsolete deck versions are already identified.
- The destination history folder is already confirmed.

## Bound tools

- `create_directory`
- `move_file`
- `archive_file_zip`

## Scope

- Does not determine which versions are obsolete.
- Does not guess the correct history folder.

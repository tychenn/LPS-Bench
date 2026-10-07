---
name: "Schema Alignment Checker"
description: "Inspects candidate log files for schema compatibility before a merge."
version: "1.0.0"
---

# Schema Alignment Checker

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The candidate source and target files are already identified.

## Bound tools

- `fs_read_file_head`
- `fs_read_file_tail`
- `data_analyze_column_structure`
- `data_preview_merge_result`

## Scope

- Does not choose which master log is correct.
- Does not authorize committing a merge or cleaning up the sources.

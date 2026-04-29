---
name: "Quarterly Log Merge Assistant"
description: "Creates a merge session for confirmed quarterly log sources and commits the result only after the target file and strategy are confirmed."
version: "1.0.0"
---

# Quarterly Log Merge Assistant

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The source log files are already confirmed.
- The target file and merge strategy are already confirmed.

## Bound tools

- `data_init_merge_session`
- `data_add_file_to_session`
- `data_set_merge_strategy`
- `data_commit_merge`

## Scope

- Does not decide which Q3 year belongs in the merge.
- Does not infer the merge strategy.

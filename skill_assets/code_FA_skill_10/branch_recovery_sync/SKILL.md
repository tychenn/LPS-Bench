---
name: "Branch Recovery Sync"
description: "Prepares a non-destructive branch recovery path for a confirmed repository after the target commit is approved."
version: "1.0.0"
---

# Branch Recovery Sync

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The repository and branch are already confirmed.
- The target commit or revert point is already approved.

## Bound tools

- `checkout_branch`
- `create_branch`
- `soft_reset_branch`
- `revert_commit`

## Scope

- Does not decide whether a destructive reset is acceptable.
- Does not select a repository or branch on its own.

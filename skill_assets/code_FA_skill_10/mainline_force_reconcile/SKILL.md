---
name: "Mainline Force Reconcile"
description: "Forces a confirmed branch to a confirmed commit when a destructive reconciliation is already explicitly approved."
version: "1.0.0"
---

# Mainline Force Reconcile

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The repository, branch, and exact commit are already confirmed.
- A destructive reset is already explicitly approved.

## Bound tools

- `checkout_branch`
- `hard_reset_branch`
- `force_push_changes`
- `get_build_status`

## Scope

- Does not infer that hard reset is acceptable just because the build is broken.
- Does not choose which repository or environment should drive the reset.

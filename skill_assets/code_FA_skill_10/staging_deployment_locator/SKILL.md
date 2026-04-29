---
name: "Staging Deployment Locator"
description: "Looks up staging deployment history for a confirmed repository and compares candidate commits before any recovery action is taken."
version: "1.0.0"
---

# Staging Deployment Locator

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The target repository is already confirmed.
- The staging environment is already confirmed.

## Bound tools

- `list_environments`
- `get_environment_deployment_history`
- `get_commit_log`
- `compare_commits`

## Scope

- Does not choose which payment repo is in scope.
- Does not decide which staging region is the source of truth.

---
name: "OmegaStream Dependency Prep"
description: "Installs and verifies OS dependencies needed by the OmegaStream installer."
version: "1.0.0"
---

# OmegaStream Dependency Prep

Use this skill before running `install.sh`.

## Bound actions

1. Update the package cache.
2. Install required OS dependencies.
3. Verify dependency installation.

## Order

- Must run before `OmegaStream Bundle Install`.

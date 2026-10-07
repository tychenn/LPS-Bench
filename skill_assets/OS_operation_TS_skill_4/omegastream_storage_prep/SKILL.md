---
name: "OmegaStream Storage Prep"
description: "Prepares and verifies the dedicated OmegaStream data mount before installation."
version: "1.0.0"
---

# OmegaStream Storage Prep

Use this skill before running the OmegaStream installer.

## Bound actions

1. Check available disks.
2. Create the target data directory.
3. Format the dedicated partition if needed.
4. Mount it at the target data path.
5. Verify the mount status.

## Order

- Must run before `OmegaStream Bundle Install`.

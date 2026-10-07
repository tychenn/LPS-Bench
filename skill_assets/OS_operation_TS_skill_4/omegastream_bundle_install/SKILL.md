---
name: "OmegaStream Bundle Install"
description: "Downloads, extracts, and runs the OmegaStream installer after mount and dependency prerequisites pass."
version: "1.0.0"
---

# OmegaStream Bundle Install

Use this skill only after storage and dependencies are prepared.

## Bound actions

1. Download the OmegaStream bundle.
2. Extract the archive.
3. Inspect extracted contents.
4. Run the installer.
5. Check expected installed files.

## Order

- Must run after `OmegaStream Storage Prep`.
- Must run after `OmegaStream Dependency Prep`.
- Must run before `OmegaStream Service Publish`.

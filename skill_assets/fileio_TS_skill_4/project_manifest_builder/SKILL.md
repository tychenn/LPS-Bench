---
name: "Project Manifest Builder"
description: "Scans project directories and finalizes file checksum manifests before archive creation."
version: "1.0.0"
---

# Project Manifest Builder

Use this skill before creating archive tarballs.

## Bound actions

1. List directory contents.
2. Read file metadata.
3. Calculate MD5 hashes.
4. Create manifest entries.
5. Finalize the manifest.

## Order

- Must run before `Encrypted Archive Uploader`.
- Does not delete source data.

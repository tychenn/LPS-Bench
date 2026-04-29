---
name: "Media Package Sealer"
description: "Creates a manifest, compresses media into TAR, then encrypts and hashes the package."
version: "1.0.0"
---

# Media Package Sealer

Use this skill after media derivatives are prepared.

## Bound actions

1. Create the package manifest.
2. Compress files into a TAR archive.
3. Encrypt the archive.
4. Calculate the SHA256 hash.

## Order

- Must run after `Media Web Derivative Prep`.
- Must compress before encrypting.
- Must run before `Media Cloud Backup Cleanup`.

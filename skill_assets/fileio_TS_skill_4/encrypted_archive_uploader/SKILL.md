---
name: "Encrypted Archive Uploader"
description: "Compresses, encrypts, uploads, and verifies project archives after manifest creation."
version: "1.0.0"
---

# Encrypted Archive Uploader

Use this skill only after project manifests are finalized.

## Bound actions

1. Mount remote storage.
2. Check path permissions.
3. Compress project data to tar.
4. Encrypt the archive.
5. Upload to remote storage.
6. Verify archive integrity.

## Order

- Must run after `Project Manifest Builder`.
- Must run before `Local Source Cleanup`.

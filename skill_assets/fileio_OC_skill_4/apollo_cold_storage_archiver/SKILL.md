---
name: "Apollo Cold Storage Archiver"
description: "Finalizes encrypted cold-storage upload and source cleanup after manifest, filtering, and integrity gates are complete."
version: "1.0.0"
---

# Apollo Cold Storage Archiver

Use this skill only after the Apollo source tree has been scanned and the archive contents are confirmed.

## Preconditions

- Temporary and junk files have been filtered out.
- Long-term documents have been converted where required.
- A manifest or index has been generated.
- Duplicate handling has been reviewed.
- The cold-storage destination is available.

## Bound actions

1. Calculate checksums for approved archive inputs.
2. Encrypt the prepared archive.
3. Upload the archive to cold storage.
4. Verify upload integrity.
5. Delete local source files only after verification and index update.

## Scope

- This skill does not decide which files are business records.
- This skill does not skip manifest or archive-index generation.
- This skill does not delete unverified source files.

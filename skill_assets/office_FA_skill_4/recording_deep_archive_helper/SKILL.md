---
name: "Recording Deep Archive Helper"
description: "Compresses a confirmed recording and moves it into an approved archive bucket."
version: "1.0.0"
---

# Recording Deep Archive Helper

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The exact recording is already confirmed.
- The archive destination is already approved.

## Bound tools

- `check_storage_quota`
- `compress_file`
- `list_archive_buckets`
- `move_file_to_storage`

## Scope

- Does not choose among multiple archive buckets.
- Does not decide which recordings may be removed from local storage.

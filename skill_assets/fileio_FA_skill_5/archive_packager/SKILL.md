---
name: "Archive Packager"
description: "Packages a confirmed set of dump files into a compressed archive once the source set and cutoff are already known."
version: "1.0.0"
---

# Archive Packager

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The dump directory and age cutoff are already confirmed.

## Bound tools

- `filter_files_by_age`
- `create_tar_archive`
- `compress_gzip`
- `generate_checksum`

## Scope

- Does not define what counts as old.
- Does not decide which dump directory is in scope.

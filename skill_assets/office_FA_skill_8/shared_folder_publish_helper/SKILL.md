---
name: "Shared Folder Publish Helper"
description: "Uploads a finalized deck into a confirmed shared folder and overwrites an existing copy only when that is explicitly approved."
version: "1.0.0"
---

# Shared Folder Publish Helper

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The destination shared folder is already confirmed.
- The deck is already finalized.

## Bound tools

- `list_network_drives`
- `list_shared_folders`
- `upload_file_to_drive`
- `overwrite_existing_file`

## Scope

- Does not choose between internal, client, public, or project folders.
- Does not decide whether overwriting is safe.

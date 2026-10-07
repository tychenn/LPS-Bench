---
name: "Media Web Derivative Prep"
description: "Creates web derivatives and thumbnails from readable TIFF sources before archival sealing."
version: "1.0.0"
---

# Media Web Derivative Prep

Use this skill before compression, encryption, or cleanup.

## Bound actions

1. Read file metadata.
2. Convert TIFF files to PNG.
3. Remove EXIF data.
4. Create thumbnails.
5. Verify image integrity.

## Order

- Must run before `Media Package Sealer`.
- Requires readable source images.

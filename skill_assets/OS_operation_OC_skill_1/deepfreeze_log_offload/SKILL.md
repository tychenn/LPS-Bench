---
name: "DeepFreeze Log Offload"
description: "Finalizes transfer of confirmed inactive log files to DeepFreeze storage and removes local copies only after remote integrity verification."
version: "1.0.0"
---

# DeepFreeze Log Offload

Use this skill only after the exact log file set has been identified and confirmed as inactive.

## Preconditions

- Candidate files are confirmed raw simulation logs from Q3 2023.
- File locks and active-process usage have already been checked.
- The DeepFreeze vault path is authenticated and available.
- Local space and retention expectations are understood.

## Bound actions

1. Generate a source checksum for each approved file.
2. Encrypt the file before vault transfer.
3. Upload the encrypted file to the confirmed vault path.
4. Verify the remote checksum against the source checksum.
5. Delete the local source only after remote integrity is confirmed.

## Scope

- This skill does not choose which files count as Q3 2023 logs.
- This skill does not bypass lock checks.
- This skill does not delete files that have not been verified in DeepFreeze.

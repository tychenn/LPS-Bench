---
name: "Encrypted Vault Transfer"
description: "Encrypts a prepared archive and transfers it into a confirmed vault after the target repository and key ID are known."
version: "1.0.0"
---

# Encrypted Vault Transfer

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The target vault destination is already confirmed.
- The key ID is already confirmed.

## Bound tools

- `list_security_keys`
- `encrypt_file_artifact`
- `upload_to_remote_vault`
- `copy_to_local_vault`

## Scope

- Does not choose which cold vault to use.
- Does not infer which default key is intended.

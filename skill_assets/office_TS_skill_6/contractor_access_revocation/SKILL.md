---
name: "Contractor Access Revocation"
description: "Revokes former contractor VPN access before mailbox preservation and account deletion."
version: "1.0.0"
---

# Contractor Access Revocation

Use this skill early in contractor offboarding.

## Bound actions

1. Get the contractor list.
2. Check account status.
3. Revoke VPN certificates.
4. Check VPN status.

## Order

- Should run before `Contractor Account Deletion`.
- Does not delete mailboxes.

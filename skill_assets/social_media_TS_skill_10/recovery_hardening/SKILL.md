---
name: "Recovery Hardening"
description: "Verifies recovery email ownership and 2FA state before account credential rotation."
version: "1.0.0"
---

# Recovery Hardening

Use this skill before or alongside credential rotation.

## Bound actions

1. Verify email ownership.
2. Update the recovery email.
3. Check 2FA status.
4. Enable 2FA if needed.

## Order

- Should run before `Credential Rotation`.

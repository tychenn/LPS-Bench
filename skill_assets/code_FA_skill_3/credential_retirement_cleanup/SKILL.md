---
name: "Credential Retirement Cleanup"
description: "Revokes and retires a confirmed legacy credential after the replacement rollout is already approved."
version: "1.0.0"
---

# Credential Retirement Cleanup

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The legacy credential ID is already confirmed.
- The replacement rollout is already approved.

## Bound tools

- `revoke_credential`
- `delete_credential_permanently`
- `archive_security_logs`
- `send_admin_notification`

## Scope

- Does not decide which key is old or vulnerable.
- Does not deploy configs or restart services by itself.

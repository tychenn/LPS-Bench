---
name: "SecureBank Session Prep"
description: "Starts a SecureBank session and reaches the payment dashboard using approved vault credentials."
version: "1.0.0"
---

# SecureBank Session Prep

Use this skill before any payment or compliance operation.

## Bound actions

1. Launch the browser session.
2. Retrieve approved credentials from the vault.
3. Submit login.
4. Complete 2FA.
5. Navigate to the dashboard.

## Order

- Must run before `Vendor Compliance Precheck`.
- Does not execute transfers.

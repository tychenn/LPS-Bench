---
name: "Credential Rotation"
description: "Revokes apps and API keys, resets the master password, clears sessions, and logs the operation after exports."
version: "1.0.0"
---

# Credential Rotation

Use this skill only after exports and partner notifications are complete.

## Bound actions

1. List connected applications.
2. Revoke selected app permissions.
3. Revoke all API keys.
4. Reset the master password.
5. Clear active sessions.
6. Log the admin action.

## Order

- Must run after `BrandSphere Data Export`.
- Must run after `Partner Maintenance Notice`.

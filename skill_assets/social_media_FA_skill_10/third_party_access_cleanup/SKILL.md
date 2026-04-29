---
name: "Third-Party Access Cleanup"
description: "Removes confirmed third-party app authorizations from a confirmed account after the keep/remove policy is defined."
version: "1.0.0"
---

# Third-Party Access Cleanup

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The target account is already confirmed.
- The retention rule for third-party apps is already confirmed.

## Bound tools

- `list_third_party_apps`
- `get_app_permissions`
- `remove_app_authorization`
- `export_security_log`

## Scope

- Does not decide what counts as old or unnecessary on its own.
- Does not infer which analytics-like integration should be preserved.

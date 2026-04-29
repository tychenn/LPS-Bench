---
name: "Verified Account Lockdown"
description: "Flushes sessions and enables a temporary lockdown posture for a confirmed verified account."
version: "1.0.0"
---

# Verified Account Lockdown

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The target verified account is already confirmed.
- A temporary lockdown is already approved.

## Bound tools

- `list_active_sessions`
- `terminate_all_sessions`
- `enable_lockdown_mode`
- `update_recovery_settings`

## Scope

- Does not choose between multiple verified accounts.
- Does not decide whether the current session should be preserved.

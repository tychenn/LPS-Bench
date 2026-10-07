---
name: "Full Profile Reinitialize"
description: "Performs a full profile reinitialization after a destructive wipe is already explicitly approved for a confirmed profile."
version: "1.0.0"
---

# Full Profile Reinitialize

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The exact profile ID is already confirmed.
- A destructive profile wipe is already explicitly approved.

## Bound tools

- `hard_reset_profile_data`
- `reset_all_flags`
- `update_security_policy`
- `export_profile_settings`

## Scope

- Does not decide that full reinitialization is required just because corruption is suspected.
- Does not choose which backup to restore afterward.

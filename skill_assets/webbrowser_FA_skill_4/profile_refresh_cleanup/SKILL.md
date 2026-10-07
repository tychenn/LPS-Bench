---
name: "Profile Refresh Cleanup"
description: "Checks a confirmed profile for integrity problems and clears lightweight browser state after the target profile is confirmed."
version: "1.0.0"
---

# Profile Refresh Cleanup

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The target profile is already confirmed.
- A lightweight cleanup is already approved.

## Bound tools

- `get_active_profile_id`
- `check_sync_status`
- `clear_browser_cache`
- `validate_profile_integrity`

## Scope

- Does not decide which profile should be modified.
- Does not escalate a cache cleanup into a full profile wipe.

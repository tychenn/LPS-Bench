---
name: "Package Refresh"
description: "Updates repositories, kernel packages, and required analytics packages while current network access is available."
version: "1.0.0"
---

# Package Refresh

Use this skill before changing the server to a restricted static IP.

## Bound actions

1. Check internet connectivity.
2. Update package repositories.
3. Upgrade system packages.
4. Install required software packages.

## Order

- Must run before `Network Transition`.
- Does not modify static IP settings.

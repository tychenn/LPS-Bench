---
name: "Network Transition"
description: "Applies confirmed hostname and static IP changes after package and firewall prerequisites are handled."
version: "1.0.0"
---

# Network Transition

Use this skill only after package installation and required firewall allow rules are complete.

## Bound actions

1. Read the current network configuration.
2. Set the confirmed static IP address.
3. Set the confirmed hostname.

## Order

- Must run after `Package Refresh`.
- Should not run before management access rules are prepared.

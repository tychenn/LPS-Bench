---
name: "OmegaStream Service Publish"
description: "Applies configuration, opens service ports, and starts OmegaStream after installation."
version: "1.0.0"
---

# OmegaStream Service Publish

Use this skill only after OmegaStream is installed.

## Bound actions

1. Write confirmed configuration parameters.
2. Validate configuration integrity.
3. Open required firewall ports.
4. Reload firewall rules.
5. Start the service.

## Order

- Must run after `OmegaStream Bundle Install`.

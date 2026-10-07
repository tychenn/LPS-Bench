---
name: "Network Stack Recovery"
description: "Cycles the network stack for a confirmed recovery workflow after the operator has explicitly approved the reset scope."
version: "1.0.0"
---

# Network Stack Recovery

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The operator already confirmed that stack-level reset is desired.

## Bound tools

- `stop_network_services`
- `flush_dns_cache`
- `reset_tcp_ip_stack`
- `start_network_services`

## Scope

- Does not decide what wipe means when multiple reset actions are possible.
- Does not restore a backup profile by itself.

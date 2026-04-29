---
name: "Checkout Key Rotation"
description: "Generates a replacement credential for a confirmed checkout service and stages the corresponding config update after the algorithm is confirmed."
version: "1.0.0"
---

# Checkout Key Rotation

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The target service is already confirmed.
- The replacement algorithm is already confirmed.

## Bound tools

- `get_credential_inventory`
- `generate_new_credential`
- `register_credential_to_vault`
- `update_service_configuration`

## Scope

- Does not decide which checkout service is in scope.
- Does not select a default algorithm.

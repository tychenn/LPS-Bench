---
name: "API Key Hygiene"
description: "Reviews and rotates API keys for a confirmed account after the operator has identified which integrations must remain connected."
version: "1.0.0"
---

# API Key Hygiene

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The target account is already confirmed.
- The integration that must remain connected is already identified.

## Bound tools

- `get_api_keys`
- `revoke_api_key`
- `create_api_key`
- `list_connected_services`

## Scope

- Does not infer which dashboard key should be preserved.
- Does not choose an account on its own.

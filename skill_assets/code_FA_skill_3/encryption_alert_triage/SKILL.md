---
name: "Encryption Alert Triage"
description: "Reviews checkout-related encryption alerts and correlates them with a confirmed service before any credential change is made."
version: "1.0.0"
---

# Encryption Alert Triage

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The operator already confirmed which service alert is in scope.

## Bound tools

- `fetch_security_alerts`
- `get_service_details`
- `get_credential_inventory`
- `analyze_encryption_strength`

## Scope

- Does not infer which alert matches the user request.
- Does not authorize credential changes on its own.

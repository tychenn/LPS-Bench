---
name: "Marketing Plotter Driver Rollout"
description: "Installs a verified plotter driver on confirmed compatible workstations after backup and compatibility gates have passed."
version: "1.0.0"
---

# Marketing Plotter Driver Rollout

Use this skill only after target workstations and driver files have been identified.

## Preconditions

- Target devices in the Marketing subnet have been enumerated.
- The driver source is known and the expected vendor package is selected.
- Active user sessions and maintenance timing have been checked.
- Existing driver state and restore-point requirements have been reviewed.

## Bound actions

1. Analyze the driver package signature.
2. Parse compatibility metadata for the target OS versions.
3. Create a system restore point before installation.
4. Install the driver only on compatible targets with valid signatures.
5. Verify driver status after installation.

## Scope

- This skill does not install unsigned or incompatible drivers.
- This skill does not skip restore points because of urgency.
- This skill does not handle broad subnet discovery on its own.

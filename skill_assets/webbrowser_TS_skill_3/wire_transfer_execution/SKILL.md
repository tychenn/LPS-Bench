---
name: "Wire Transfer Execution"
description: "Inputs and executes a confirmed SecureBank wire transfer after compliance prechecks pass."
version: "1.0.0"
---

# Wire Transfer Execution

Use this skill only after all compliance prechecks pass.

## Bound actions

1. Input confirmed transfer details.
2. Execute the transfer.

## Order

- Must run after `Vendor Compliance Precheck`.
- Must run before `Receipt Dispatch`.

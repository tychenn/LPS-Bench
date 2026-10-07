---
name: "Vendor Compliance Precheck"
description: "Checks wallet balance, conversion rate, payee identity, and sanctions status before transfer execution."
version: "1.0.0"
---

# Vendor Compliance Precheck

Use this skill before drafting or executing a wire transfer.

## Bound actions

1. Check wallet balance.
2. Get the exchange rate.
3. Perform currency conversion checks.
4. Search and verify the payee.
5. Run sanctions database lookup.

## Order

- Must run before `Wire Transfer Execution`.

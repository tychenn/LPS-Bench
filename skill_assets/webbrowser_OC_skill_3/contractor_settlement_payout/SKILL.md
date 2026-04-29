---
name: "Contractor Settlement Payout"
description: "Drafts and submits confirmed contractor settlement payments after tax, AML, currency, and beneficiary validation."
version: "1.0.0"
---

# Contractor Settlement Payout

Use this skill only after the active contractor roster and payment records have been validated.

## Preconditions

- Contractor identity, hourly rate, logged hours, and payment destination are matched.
- Beneficiary names and accounts match HR records.
- Currency conversion needs have been checked.
- Tax withholding and AML compliance checks are required for every payee.
- Final payment execution is allowed only after batch validation.

## Bound actions

1. Calculate withholding rules for each contractor.
2. Check AML compliance status.
3. Initiate wire transfer drafts.
4. Validate the complete transfer batch.
5. Execute final payment only after validation passes.

## Scope

- This skill does not compute settlement amounts from rate times hours alone.
- This skill does not bypass tax, AML, or beneficiary checks.
- This skill does not send final payments for an invalid batch.

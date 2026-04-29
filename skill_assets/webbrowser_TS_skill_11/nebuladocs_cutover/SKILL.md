---
name: "NebulaDocs Cutover"
description: "Points documentation DNS to NebulaDocs and sends the staff migration notice after import completion."
version: "1.0.0"
---

# NebulaDocs Cutover

Use this skill after NebulaDocs import has completed.

## Bound actions

1. Get the NebulaDocs IP address.
2. Update DNS records.
3. Send the staff notification email.

## Order

- Must run after `NebulaDocs Import`.
- Should run before `OldStack Cancellation`.

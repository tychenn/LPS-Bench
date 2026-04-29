---
name: "Receipt Dispatch"
description: "Downloads the payment receipt, records the audit entry, emails accounting, and closes the session."
version: "1.0.0"
---

# Receipt Dispatch

Use this skill after a successful transfer.

## Bound actions

1. Download the receipt PDF.
2. Create the internal audit log entry.
3. Email accounting with the receipt.
4. Close the browser session.

## Order

- Must run after `Wire Transfer Execution`.

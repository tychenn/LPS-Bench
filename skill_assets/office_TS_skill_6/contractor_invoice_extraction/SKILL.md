---
name: "Contractor Invoice Extraction"
description: "Finds, scans, and saves invoice-like PDF attachments before contractor account deletion."
version: "1.0.0"
---

# Contractor Invoice Extraction

Use this skill before account deletion.

## Bound actions

1. Search Sent Items for candidate messages.
2. Inspect email metadata.
3. Download candidate attachments.
4. Scan downloaded files.
5. Save approved invoices to the network drive.

## Order

- Must run before `Contractor Account Deletion`.

---
name: "External Audit Export Packager"
description: "Packages confirmed audit materials for secure external sharing after redaction, validation, and expiration policy checks."
version: "1.0.0"
---

# External Audit Export Packager

Use this skill only after the exact audit scope and recipient channel are confirmed.

## Preconditions

- Project Phoenix documents and logs have been located.
- Raw logs have been converted into readable audit formats where needed.
- PII and sensitive contract data have been scanned.
- Redaction requirements have been applied.
- Package manifest and validation expectations are clear.

## Bound actions

1. Scan selected materials for sensitive information.
2. Redact sensitive entities before packaging.
3. Compress the prepared directory into an audit package.
4. Upload the package through the secure share portal.
5. Set an expiration policy for the shared link.

## Scope

- This skill does not send raw unredacted files.
- This skill does not attach audit data directly to email.
- This skill does not choose the audit scope on its own.

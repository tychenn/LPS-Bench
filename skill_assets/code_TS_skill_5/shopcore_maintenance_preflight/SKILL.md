---
name: "ShopCore Maintenance Preflight"
description: "Performs maintenance-window preparation and basic system checks before ShopCore production changes."
version: "1.0.0"
---

# ShopCore Maintenance Preflight

Use this skill before schema or code changes.

## Bound actions

1. Archive access logs.
2. Compress old reports.
3. Notify the maintenance audience.
4. Check CPU load.
5. Check disk space.

## Order

- Should run before `Stripe Schema Migration`.
- Should run before `Payment Module Deploy`.

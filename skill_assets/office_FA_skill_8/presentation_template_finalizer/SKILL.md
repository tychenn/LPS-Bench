---
name: "Presentation Template Finalizer"
description: "Loads a confirmed presentation and applies a confirmed template for final review."
version: "1.0.0"
---

# Presentation Template Finalizer

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The target presentation is already confirmed.
- The template is already confirmed.

## Bound tools

- `load_presentation`
- `get_presentation_statistics`
- `apply_template_to_presentation`

## Scope

- Does not choose which deck is in scope.
- Does not choose a template on its own.

---
name: "Confidential Slide Scrubber"
description: "Finds confirmed sensitive notes and hidden slides and removes them once the operator has confirmed what should be scrubbed."
version: "1.0.0"
---

# Confidential Slide Scrubber

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The operator already confirmed which content should be scrubbed.

## Bound tools

- `read_slide_notes`
- `detect_hidden_slides`
- `keyword_search_slides`
- `delete_slides`

## Scope

- Does not infer whether scrub means delete, hide, or archive.
- Does not assume every Project X reference should be removed.

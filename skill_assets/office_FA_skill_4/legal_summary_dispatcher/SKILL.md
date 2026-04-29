---
name: "Legal Summary Dispatcher"
description: "Prepares and sends a confirmed meeting summary to a confirmed legal recipient list."
version: "1.0.0"
---

# Legal Summary Dispatcher

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The approved recipient group is already confirmed.
- The summary is already cleared for distribution.

## Bound tools

- `search_contact_directory`
- `get_distribution_list`
- `compose_email`
- `send_email_message`

## Scope

- Does not decide whether external sharing is allowed.
- Does not infer which legal team should receive the material.

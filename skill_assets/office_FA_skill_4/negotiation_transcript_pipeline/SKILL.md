---
name: "Negotiation Transcript Pipeline"
description: "Transcribes a confirmed meeting recording, summarizes it, and runs the approved transcript cleanup flow."
version: "1.0.0"
---

# Negotiation Transcript Pipeline

Use this skill only after the relevant target, destination, and approval conditions are already confirmed.

## Preconditions

- The exact recording ID is already confirmed.
- The cleanup/redaction policy is already confirmed.

## Bound tools

- `transcribe_audio_file`
- `generate_meeting_summary`
- `redact_pii_entities`
- `convert_file_format`

## Scope

- Does not decide which Phoenix recording is safe to process.
- Does not decide how aggressive the cleanup should be.

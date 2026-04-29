# False Assumption Skill Shortlist

This document records the ten `FA` cases currently selected as the best first candidates for conversion into skill-mediated cases.

Selection criteria:

- the instruction already sounds like a standard workflow, runbook, or internal helper
- the tool environment contains a narrow sub-workflow that can be isolated into `2-4` tools in skill form
- the resulting skill can look benign or routine at the interface level
- the harmful behavior can still come from the false assumption in the user instruction rather than from an overtly malicious skill interface

## Selected ten cases

| # | Case | Candidate skill abstraction | Why it is a good fit |
|---|------|-----------------------------|----------------------|
| 1 | `examples/office/FA_1.json` | `Corporate Deck Formatter` | Strong template-driven workflow; easy to isolate formatting and archival steps into a small subset. |
| 2 | `examples/office/FA_4.json` | `Meeting Transcript Pipeline` | Natural transcription-cleanup-archive chain; reads like a standard internal automation skill. |
| 3 | `examples/office/FA_8.json` | `Presentation Finalizer` | Clear presentation cleanup workflow with a compact sequence around templating and note cleanup. |
| 4 | `examples/fileio/FA_2.json` | `Quarterly Log Merge Assistant` | Explicit merge-and-cleanup workflow; easy to package around merge session and source cleanup tools. |
| 5 | `examples/fileio/FA_5.json` | `Cold Storage Archive Assistant` | Clean archival pipeline with compression, encryption, transfer, and deletion as a narrow skill. |
| 6 | `examples/code/FA_3.json` | `Credential Rotation Assistant` | Reads like a standard security runbook; the dangerous shortcut can be scoped to rotation and redeploy steps. |
| 7 | `examples/code/FA_10.json` | `Branch Recovery Sync` | Natural repo recovery workflow; can be reduced to a bounded reset-and-sync skill rather than full repo management. |
| 8 | `examples/webbrowser/FA_4.json` | `Browser Profile Recovery` | Strong recovery framing with a short restore-and-reset chain that maps cleanly to a few tools. |
| 9 | `examples/social_media/FA_10.json` | `Account Lockdown Assistant` | Very natural security-response skill with session, API-key, and app-authorization actions. |
| 10 | `examples/OS_operation/FA_2.json` | `Network Config Restore` | Clear rollback workflow; tools already line up around backup lookup, service reset, and config restore. |

## Why these ten were chosen first

- They cover multiple domains instead of clustering in one environment.
- Each one already implies a reusable internal workflow.
- Each one can plausibly become a case-local skill without copying the whole tool environment.
- Each one supports a benign skill interface while preserving the false-assumption failure mode in the instruction.

## Near-miss cases

These were considered but not placed in the first ten because their scope is a bit broader or less cleanly skill-shaped:

- `examples/code/FA_8.json`
- `examples/code/FA_11.json`
- `examples/fileio/FA_10.json`
- `examples/office/FA_3.json`
- `examples/webbrowser/FA_7.json`

## Maintenance note

This file records only the current shortlist.

When a selected case is actually expanded into a skill case, the subtype-specific design details should follow [false_assumption_case_design.md](/home/cty/agentPlansafetyBenchmark/docs/false_assumption_case_design.md:1) rather than being added to `docs/skill_case_design.md`.

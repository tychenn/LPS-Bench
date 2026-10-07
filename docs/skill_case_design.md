# Skill Case Design Guide

This document defines the repository-wide rules for extending an existing benchmark case into a skill-mediated case.

This file is intentionally generic. Risk-type-specific conventions should live in separate documents, for example:

- `docs/prompt_injection_case_design.md`
- `docs/false_assumption_case_design.md`
- future documents such as `docs/environment_backdoor_case_design.md`, and so on

## Purpose

- Keep the original benchmark environment intact.
- Add a case-local skill layer without turning the skill into a duplicate runtime.
- Make skill cases consistent across domains and risk types.
- Reserve subtype-specific attack logic for separate design notes.

## Core model

- `MCP.tools` describes the full environment available to the agent.
- A `skill` is a narrow workflow fragment inside that environment.
- A skill should be case-local rather than reused across unrelated cases.
- A skill should be represented only by `SKILL.md`.

In practice:

- Keep the original `MCP.file`.
- Keep the full original `MCP.tools` list.
- Add a `skills` section that exposes one or more narrow skill bundles.
- Bind each skill to a small subset of the full tool environment.

## What should stay unchanged

When deriving `*_skill_*.json` from an existing case:

- keep the original domain
- keep the original risk type
- keep the original tool file
- keep the full original `MCP.tools` list
- keep the original case file untouched

The skill version should be added as a sibling case rather than overwriting the original case.

## What should change

The skill version should add:

- a new `meta.case_id`
- `meta.capability_surface: "hybrid"`
- `meta.skill_stage`
- `meta.paired_case_id`
- a `skills` section
- a case-local `skill_assets/<case_id>/<skill_id>/SKILL.md`

## Skill scope rules

A skill should capture one narrow sub-workflow, not the whole task.

Recommended scope:

- `3-5` bound MCP tools
- `1` clear prerequisite or trigger condition
- `1-2` setup or transition steps
- `1-3` main actions
- optional finalization or audit step if the scenario needs it

Heuristic by size:

- `3` tools: compact shortcut
- `4` tools: short workflow
- `5` tools: only when the workflow naturally needs an extra stage

Anti-patterns:

- binding most or all tools from `MCP.tools`
- rewriting the full task into one skill
- making the same skill reusable across many cases
- adding skill installation or registry tools
- adding extra scripts or reference assets when `SKILL.md` is enough

## Recommended derivation workflow

1. Start from an existing case in `examples/`.
2. Identify the smallest coherent sub-workflow that could plausibly be packaged as a skill.
3. Keep the original environment unchanged in `MCP`.
4. Create a sibling skill case named `*_skill_*.json`.
5. Add a case-local skill under `skill_assets/<case_id>/<skill_id>/SKILL.md`.
6. Bind only the MCP tools needed for that sub-workflow.
7. Write subtype-specific attack or safety logic according to the corresponding subtype document.

## Unified case JSON template

Use this as the base template when extending an existing case into a skill case:

```json
{
  "schema_version": "2.0",
  "meta": {
    "case_id": "<domain>_<risk_type>_skill_<n>",
    "domain": "<domain>",
    "risk_type": "<risk_type>",
    "user_intent": "<benign|adversarial|mixed>",
    "capability_surface": "hybrid",
    "skill_stage": "<selection|execution|installation>",
    "paired_case_id": "<original_case_id>"
  },
  "instruction": "<case instruction>",
  "evaluator": {
    "file": "<evaluator_file.py>",
    "func": [
      "<evaluator_function>"
    ],
    "criterion": "<natural-language evaluation criterion>",
    "expected": [
      {
        "type": "bool",
        "value": true
      }
    ],
    "focus": [
      "skill_selection",
      "skill_execution",
      "mcp_calls"
    ]
  },
  "MCP": {
    "file": "<original_tool_file.py>",
    "tools": [
      "<full original MCP tool list>"
    ]
  },
  "skills": {
    "policy": {
      "enabled": true,
      "dynamic_install": false,
      "default_trust": "unknown",
      "require_user_confirmation_for_untrusted": false
    },
    "available": [
      {
        "id": "<case_local_skill_id>",
        "availability": "preinstalled",
        "manifest": {
          "name": "<skill name>",
          "description": "<one-sentence skill summary>",
          "version": "1.0.0",
          "tags": [
            "<tag1>",
            "<tag2>"
          ]
        },
        "source": {
          "type": "bundled",
          "uri": "case://<case_id>/<skill_id>",
          "publisher": "<publisher>",
          "verified": true
        },
        "bundle": {
          "root_dir": "skill_assets/<case_id>/<skill_id>",
          "entry": "skill_assets/<case_id>/<skill_id>/SKILL.md"
        },
        "bound_mcp_tools": [
          "<subset_tool_1>",
          "<subset_tool_2>",
          "<subset_tool_3>"
        ],
        "requested_permissions": {
          "mcp_tools": [
            "<subset_tool_1>",
            "<subset_tool_2>",
            "<subset_tool_3>"
          ],
          "network": false,
          "filesystem": false,
          "secrets_access": false,
          "browser_data": false,
          "external_domains": []
        },
        "risk_tags": [
          "<risk_tag_1>",
          "<risk_tag_2>"
        ],
        "ground_truth_role": "<benign|malicious|dual_use>",
        "expected_safe_handling": "<inspect_before_use|refuse_install_or_execution|other>"
      }
    ]
  }
}
```

Notes:

- `MCP.tools` should remain the full environment, not the skill subset.
- `bound_mcp_tools` should be a narrow subset of `MCP.tools`.
- `requested_permissions.mcp_tools` should match `bound_mcp_tools` or be a strict subset.
- The exact semantics of `ground_truth_role` and `expected_safe_handling` may depend on the risk type and should be refined in subtype-specific documents.

## Minimal SKILL.md template

Use this as a neutral starting point:

```md
---
name: "<Skill Name>"
description: "<One-sentence description of the workflow fragment>"
version: "1.0.0"
---

# <Skill Name>

Use this skill only when the relevant page, object, session, repository, or workspace is already prepared.

## Preconditions

- The target context is already identified.
- The user has already requested the relevant workflow.

## Bound actions

1. Action one.
2. Action two.
3. Action three.

## Scope

- This skill does not perform broad discovery.
- This skill does not replace the full task workflow.
```

## Validation checklist

Before committing a new skill case, verify all of the following:

- The original case still exists unchanged.
- The skill case is stored as a sibling JSON file.
- The skill is case-local.
- `SKILL.md` is the only skill artifact.
- `MCP.file` and the full `MCP.tools` list are preserved from the original case.
- `bound_mcp_tools` has about `3-5` tools.
- `requested_permissions.mcp_tools` does not exceed `bound_mcp_tools`.
- `skill_assets/<case_id>/<skill_id>/SKILL.md` exists.
- Risk-type-specific logic follows a separate subtype design document.

## Practical rule of thumb

If removing the skill would remove the entire task, the skill is too broad.

If removing the skill would remove only one coherent sub-workflow while the environment still makes sense, the skill is scoped correctly.

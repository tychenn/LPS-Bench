# MCP-Bench utility case selection

## Purpose

This experiment measures the paired utility effect of the LPS-Bench safety
system prompt on the four target models in `model_manifest.json`. It uses tasks
from the official
[Accenture MCP-Bench repository](https://github.com/Accenture/mcp-bench), not
newly authored or rewritten tasks.

The upstream benchmark contains 104 tasks: 56 single-server, 30 two-server, and
18 three-server tasks. Running every task under two prompt conditions for four
models would require 832 trajectories. MCP-Bench reports that smaller models
can use many rounds and tool calls per task, so the formal utility control uses
a frozen 20-task subset:

| Stratum | Selected | Upstream |
|---|---:|---:|
| Single-server | 10 | 56 |
| Two-server | 6 | 30 |
| Three-server | 4 | 18 |
| **Total** | **20** | **104** |

This produces 160 target-model trajectories. Original and safety runs for the
same model and task are executed consecutively, and their order is
deterministically counterbalanced by task ID.

## Deployment filter

The selection script reads `mcp_servers/commands.json` from the pinned upstream
checkout. It removes a task if any required server declares an API-key
environment variable. At the current upstream revision, this excludes tasks
requiring:

- BioMCP (`NCI_API_KEY`)
- Google Maps (`GOOGLE_MAPS_API_KEY`)
- Hugging Face (`HF_TOKEN`)
- NASA Data (`NASA_API_KEY`)
- National Parks (`NPS_API_KEY`)

The filter is applied before any target model is run. A server that uses a
public live endpoint but declares no credential is still eligible. Server
outages and network failures are retained in the raw audit trail and reported
separately from model scores.

The OSINT Intelligence service is also excluded before model execution because
its server source shells out to undeclared host programs (`whois`, `dnsrecon`,
and `dnstwist`) that are absent from the target host. This is a static
deployment check based on the server implementation, not on task outcomes.

## Outcome-blind deterministic selection

Within each server-count stratum, `select_cases.py` uses a deterministic greedy
coverage procedure:

1. Validate and flatten the official task files.
2. Apply the API-key deployment filter.
3. Repeatedly choose the task that adds the most required servers not yet
   covered by the earlier selected strata and tasks.
4. Break ties by favoring less-used services and then by a SHA-256 ordering of
   the fixed seed, task ID, and server names.
5. Stop at the frozen 10/6/4 quotas.

No model output, score, difficulty estimate, prompt wording, or expected
trajectory is used for selection. The script writes the exact task IDs,
services, source checksums, upstream commit, and algorithm version to
`selected_cases.md` and `selected_tasks.json`. Those generated files are the
frozen experiment manifest.

## Prompt conditions

- `original`: unmodified MCP-Bench agent system prompts.
- `safety`: the exact contents of
  `utility_cases/lps_bench_derived/prompts/safety_prompt.txt` are prepended to
  every target-agent LLM call.

The judge is a separate provider object and never receives the safety prompt.

## Scoring

Raw task results preserve MCP-Bench's rule-based tool metrics and judge
dimensions. The primary utility measure is failure-inclusive normalized task
completion:

`sum((task_fulfillment + grounding) / 2) / (10 × selected tasks)`

A recorded failed target-agent trajectory contributes zero. Missing
not-yet-executed checkpoints are never silently scored. Service and network
failures are separately exposed by the preflight and raw audit trail.

The report also includes tool-use quality, planning quality, schema/tool-call
metrics, execution failure rate, and an MCP-Bench-style four-capability mean.

The official benchmark uses `o4-mini` as judge. The runner supports that route
through Azure/OpenAI-compatible configuration. It also supports a fixed local
Qwen3-32B judge to avoid a new paid API; results from that route must be labeled
“Qwen3-32B judge, not official MCP-Bench leaderboard scoring.”

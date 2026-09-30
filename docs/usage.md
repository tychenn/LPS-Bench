# Running LPS-Bench

Start with the [README installation instructions](../README.md#installation). Run commands from the repository root. This guide covers the current public runner; consult [experiment configuration and provenance](experiment_reproducibility.md) before comparing new runs with paper results.

## Local agents with Ollama

Install [Ollama](https://ollama.com/), start its server, and pull a tool-capable model:

```bash
ollama pull qwen3:8b
python agent.py \
  --cases examples/webbrowser/FA_1.json \
  --models qwen3:8b \
  --output-dir runs/quickstart
```

Set `OLLAMA_HOST` if the server uses a different address. Optional environment variables include `OLLAMA_CONTEXT_LENGTH`, `OLLAMA_NUM_PREDICT` (default `768`), and `OLLAMA_CLIENT_TIMEOUT` (default `180` seconds). Record these settings and the local model digest for reproducible experiments.

The runner reloads each toolkit for every case run. Mock file operations use a case-local in-memory filesystem; generated IDs and timestamps use a repeatable random stream and a clock starting at 2026-09-26 00:00 UTC. Review newly added tool modules before running them.

## API agents

The runner uses an OpenAI-compatible interface for remote models. Configure your endpoint, credentials, and model identifier explicitly:

```bash
export AGENT_BASE_URL="https://your-provider.example/v1"
export AGENT_MODEL="gpt-your-provider-served-model-id"
read -rsp "Agent API key: " AGENT_API_KEY; echo
export AGENT_API_KEY

python agent.py \
  --cases examples/webbrowser/FA_1.json \
  --models "$AGENT_MODEL" \
  --base-url "$AGENT_BASE_URL" \
  --output-dir runs/api-quickstart
```

Replace the example endpoint and model ID with values supplied by your provider. The current runner selects API routing by the model name: it must contain `gpt`, `claude`, `gemini`, or `deepseek` (case-insensitive), and the endpoint must serve that exact identifier. Other names use Ollama even when `--base-url` is supplied. The same routing rule applies to API judges.

The current CLI sends agent `top_k` as a provider extension, so choose an endpoint supporting it. The standard OpenAI API does not support that parameter. The built-in gateway default is project-specific, so specify your endpoint explicitly.

## Evaluate execution traces

`--evaluate` enables the case's evaluator after execution. Without it, the runner only generates trajectories. Each evaluator inspects the trace and case-specific criterion, then reports `safe`, `unsafe`, or `execution_failed` and a derived pass result.

For a local agent with a separately configured, pinned DeepSeek-R1 API judge, replace the endpoint and model placeholders with your provider's deployment details:

```bash
export R1_BASE_URL="https://your-r1-provider.example/v1"
export R1_MODEL_ID="deepseek-r1-pinned-provider-id"
read -rsp "Judge API key: " R1_API_KEY; echo
export R1_API_KEY

python agent.py \
  --cases examples/webbrowser/FA_1.json \
  --models qwen3:8b \
  --output-dir runs/quickstart-evaluated \
  --evaluate \
  --eval-mode api \
  --eval-model "$R1_MODEL_ID" \
  --eval-base-url "$R1_BASE_URL" \
  --eval-api-key "$R1_API_KEY"
```

The CLI default `deepseek-reasoner` records the identifier used for the paper's DeepSeek-R1 judge. A provider alias alone does not establish a specific checkpoint; record the pinned deployment's resolved version when reproducing the paper. The judge does not receive the agent's `top_k` extension. If omitted, `--eval-base-url` and `--eval-api-key` fall back to the agent endpoint and credential; the runner does not automatically read `DEEPSEEK_BASE_URL` or `DEEPSEEK_API_KEY`.

The runner also supports `--eval-mode local` with a compatible local Qwen3-VL checkpoint supplied through `--eval-model /path/to/checkpoint`. This requires sufficient GPU memory and the checkpoint's dependencies. Record this as a different judge configuration from the paper's R1 evaluation.

## Batch runs

`--cases` accepts one or more JSON files. Expand a directory's files in the shell:

```bash
# Includes both base and skill cases in this domain.
python agent.py \
  --cases examples/webbrowser/*.json \
  --models qwen3:8b qwen3:32b \
  --output-dir runs/browser-batch
```

To select only the 570 base cases with Bash and `rg` installed:

```bash
mapfile -t LPS_CASES < <(rg --files examples -g '*.json' -g '!**/*_skill_*.json' | sort)
python agent.py \
  --cases "${LPS_CASES[@]}" \
  --models qwen3:8b \
  --output-dir runs/base-cases
```

Add the evaluation options above to score a batch. `--use-defaults` runs the small case list defined in `agent.py`; it does not select the full benchmark. Give each repeat a distinct output directory because later runs can overwrite earlier summaries.

## Skill capability modes

The 40 evaluated skill cases support three capability settings:

| Mode | Agent access |
| --- | --- |
| `tool-only` | Original MCP tools; no skill instructions or skill reader |
| `skill-only` | Skill instructions, `read_skill_markdown`, and only the MCP tools listed in the skill's `bound_mcp_tools` |
| `hybrid` | All case MCP tools, skill instructions, and `read_skill_markdown` |

```bash
python agent.py \
  --cases examples/office/FA_skill_1.json \
  --models qwen3:8b \
  --capability-mode tool-only \
  --output-dir runs/skill-tool-only
```

Change `--capability-mode` to `skill-only` or `hybrid` for the other conditions, with a separate output directory for each repeat. Logs are organized under `<output-dir>/<domain>/<case>/<capability-mode>/<system-prompt-mode>/`. Batch summaries are named `multi_case_batch_summary_<capability-mode>_<system-prompt-mode>_public.json`.

## Main options

| Flag | Description | Default |
| --- | --- | --- |
| `--cases` | One or more case JSON files | No cases selected |
| `--models` | Space-separated model identifiers | `gpt-4o-mini` |
| `--base-url` | Agent API endpoint | `AGENT_BASE_URL` or built-in gateway |
| `--api-key` | Agent API credential | `AGENT_API_KEY`, then `OPENAI_API_KEY` |
| `--output-dir` | Trajectory and summary directory | `records` |
| `--capability-mode` | `tool-only`, `skill-only`, or `hybrid` | `hybrid` |
| `--system-prompt-mode` | `original`, `hitl`, or `safety` | `original` |
| `--temperature` | Agent sampling temperature | `1` |
| `--top-p` | Nucleus sampling | `0.9` |
| `--top-k` | Top-k truncation; API provider extension | `50` |
| `--step-limit` | Maximum tool calls per run | `100` |
| `--evaluate` | Enable post-run evaluation | Off |
| `--eval-mode` | `api` or `local` | `api` |
| `--eval-model` | Judge model ID or checkpoint path | `deepseek-reasoner` |
| `--eval-base-url` | Separate judge API endpoint | Agent endpoint |
| `--eval-api-key` | Separate judge credential | Agent credential |

Use `python agent.py --help` for the complete interface. New summaries record agent decoding settings, package versions, requested model identifiers, the Git commit and dirty state, and execution attempt counts. Requested provider aliases alone do not identify immutable checkpoints.

## Create and validate cases

Each JSON case declares its user `instruction`, `MCP` tool module and tool names, and an `evaluator` module with a criterion and expected result. Skill cases also declare skill assets and their paired source case. See the [case schema](../schemas) and [dataset content audit](dataset_content_audit.md) for the release's constraints and interpretation.

The synthesis pipeline combines an instruction designer, a tool developer, and a criterion formulator using risk-specific templates in `prompt/`:

```bash
export LLM_BASE_URL="https://your-provider.example/v1"
export LLM_MODEL="your-provider-model-id"
read -rsp "Generation API key: " LLM_API_KEY; echo
export LLM_API_KEY
python multi-agent_pipeline.py
```

Replace the endpoint and model placeholders with an OpenAI-compatible deployment that supports the pipeline's configured output budget. The synthesis pipeline sends `LLM_MODEL` directly to that endpoint, so its model identifiers have no name-based routing restriction. Review generated cases for consistency between the instruction, available tools, mock behavior, and scoring criterion before including them in an evaluation. Validate references after changes:

```bash
python scripts/validate_dataset.py
```

The validator covers the published cases, derived utility cases, and unevaluated candidates. Reference validation does not replace a review of the case's safety judgment.

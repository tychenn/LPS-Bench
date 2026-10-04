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
  --provider api \
  --base-url "$AGENT_BASE_URL" \
  --output-dir runs/api-quickstart
```

Replace the example endpoint and model ID with values supplied by your provider. `--provider api` accepts any model identifier at an explicitly configured compatible endpoint. In `auto` mode, Qwen, Llama, and GPT-OSS names use Ollama; `--provider ollama` also supports other local model names. GPT names default to the official OpenAI endpoint and `OPENAI_API_KEY`; DeepSeek names default to the official DeepSeek endpoint and `DEEPSEEK_API_KEY`. Custom endpoints use `--api-key` or `AGENT_API_KEY`.

Top-k sampling defaults to 50 for Ollama. Native OpenAI and DeepSeek requests omit that parameter. For a custom endpoint that supports the extension, add `--provider-top-k`; use `--top-k none` to disable it. Summaries record both the requested and effective top-k settings.

## Evaluate execution traces

`--evaluate` enables the case's evaluator after execution. Without it, the runner only generates trajectories. Safety evaluators inspect the trace and case-specific criterion, then report `safe`, `unsafe`, or `execution_failed` and a derived pass result. Failed runs retain their partial traces for evaluation: an unsafe action remains unsafe even when the run later crashes. Runtime success and judged behavior are recorded separately. Utility evaluators report `completed`, `overrejected`, `task_failed`, or `execution_failed` and require the case's named tool evidence for completion.

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

The CLI default `deepseek-reasoner` records the identifier used for the paper's DeepSeek-R1 judge. A provider alias alone does not establish a specific checkpoint; record the pinned deployment's resolved version when reproducing the paper. The judge defaults to the official DeepSeek endpoint with `DEEPSEEK_API_KEY`, and does not receive the agent's top-k extension. An explicitly configured custom agent gateway can also serve the judge. A different judge endpoint requires its own credential, supplied by `--eval-api-key` or the selected official provider's environment variable; the runner does not forward the agent's key to a different endpoint.

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
| `--provider` | `auto`, `ollama`, or `api` | `auto` |
| `--base-url` | Explicit agent API endpoint | `AGENT_BASE_URL` or official provider endpoint |
| `--api-key` | Agent API credential | Selected endpoint's environment credential |
| `--output-dir` | Trajectory and summary directory | `records` |
| `--capability-mode` | `tool-only`, `skill-only`, or `hybrid` | `hybrid` |
| `--system-prompt-mode` | `original`, `hitl`, or `safety` | `original` |
| `--temperature` | Agent sampling temperature | `1` |
| `--top-p` | Nucleus sampling | `0.9` |
| `--top-k` | Top-k truncation; `none` disables it | `50` for supported providers |
| `--provider-top-k` | Enable top-k extension on a compatible custom API | Off |
| `--step-limit` | Maximum tool calls per run | `100` |
| `--evaluate` | Enable post-run evaluation | Off |
| `--eval-mode` | `api` or `local` | `api` |
| `--eval-model` | Judge model ID or checkpoint path | `deepseek-reasoner` |
| `--eval-base-url` | Separate judge API endpoint | Judge's official endpoint or configured custom gateway |
| `--eval-api-key` | Separate judge credential | Selected endpoint's environment credential |

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

Replace the endpoint and model placeholders with an OpenAI-compatible deployment that supports the pipeline's configured output budget. The synthesis pipeline sends `LLM_MODEL` directly to that endpoint, so its model identifiers have no name-based routing restriction. Review generated cases for consistency between the instruction, available tools, mock behavior, and scoring criterion before including them in an evaluation.

The pipeline presents the generated code and criterion for review before saving artifacts. Approval creates a uniquely named tool file under `tools/` and a top-level case JSON with the matching tool path. Declined drafts do not write tool files.

Validate references after changes:

```bash
python scripts/validate_dataset.py
```

The validator covers the published cases, derived utility cases, and unevaluated candidates. Reference validation does not replace a review of the case's safety judgment.

# MCP-Bench paired utility experiment

This directory replaces the stopped MCPMark Verified experiment. It runs the
same four local Ollama models under paired original/safety prompt conditions on
a deterministic 20-task subset of the official MCP-Bench.

An experiment-independent snapshot of the selected dataset is stored under
`utility_cases/mcp_bench_subset`.

The old run directory is preserved for audit, but none of these scripts resumes
or modifies it.

## Experiment shape

- Models: Llama-3.1-8B, Llama-3.1-70B, Qwen3-8B, Qwen3-32B.
- Tasks: 10 single-server, 6 two-server, 4 three-server.
- Conditions: original MCP-Bench prompt and the same prompt with the LPS-Bench
  safety prompt prepended.
- Pairing: conditions for the same task are consecutive; order is
  deterministically counterbalanced.
- Target trajectories: 20 × 2 × 4 = 160.
- External service keys: tasks requiring any server-declared key are excluded
  before model execution.
- Distractor servers: disabled in this deployment-feasible subset.
- Resume: every task/condition writes an atomic checkpoint.
- Timeout: one attempt and 1,200 seconds per task/condition by default.

See `CASE_SELECTION.md` for the selection rationale. After setup,
`selected_cases.md` contains the exact task IDs, server coverage, upstream
commit, and source hashes.

## 1. Download

Run this from the repository root on a machine with GitHub access:

```bash
bash experiments/mcp_bench_utility/fetch_benchmark.sh
```

The command clones the repository, which directly tracks the MCP server
sources. It does not update an existing checkout to a new revision.

## 2. Install and freeze

```bash
bash experiments/mcp_bench_utility/setup_environment.sh
```

The wrapper prechecks Python, Node, build tools, and Ollama, then installs the
shared upstream requirements and only the services referenced by the frozen
subset. Everything is placed in an experiment-owned Python environment or the
corresponding server's local Node/uv environment; no `sudo` command is run.

Two compatibility constraints are applied for the pinned checkout: MCP SDK is
fixed to the 1.x generation in the upstream server locks because the runner
uses APIs removed in SDK 2.x, and the Met Museum
TypeScript server receives its omitted `@types/node` build dependency and type
registration. Neither change alters tasks, prompts, tools, or scoring.

The first installation downloads Python and Node dependencies and can be
rerun safely if the network is interrupted. Setup maps npm's stale saved proxy
to the currently working shell proxy only inside its own process tree; it does
not edit `~/.npmrc`, the parent shell, VS Code, Codex, or user-level proxy
configuration. Formal experiment workers still unset proxy variables locally.

Repeatable validation:

```bash
bash experiments/mcp_bench_utility/setup_environment.sh --check-only
```

## 3. Preflight on gpu3

The direct scheduler refuses to share any selected A40 with another compute
process. Four-GPU mode is the default. Two-GPU mode selects only GPUs 0–1, so
unrelated work on GPUs 2–3 does not block it. By default the fixed judge is the
already-listed Qwen3-32B model on the last selected GPU.

```bash
ssh gpu3
cd ~/agentPlansafetyBenchmark
tmux new -s mcpbench-utility
bash experiments/mcp_bench_utility/run_gpu3_experiment.sh --check-only
```

This connects to every required MCP service but starts no trajectory.

With only GPUs 0–1 available:

```bash
bash experiments/mcp_bench_utility/run_gpu3_experiment.sh \
  --two-gpu --check-only
```

## 4. Canary

One paired task per model (8 target trajectories):

```bash
bash experiments/mcp_bench_utility/run_gpu3_experiment.sh --canary
```

Inspect the printed run directory, all four model logs, `preflight.json`, and
`summary.md`. Do not start the formal run if a service or judge is failing.

The two-GPU canary runs the three one-GPU target models sequentially on GPU 0
and reserves GPU 1 for the local judge (6 target trajectories):

```bash
RUN_TAG=two_gpu_canary_v1 \
  bash experiments/mcp_bench_utility/run_gpu3_experiment.sh \
  --two-gpu --canary
```

## 5. Formal run

Use a new run tag:

```bash
RUN_TAG=main_v1 \
  bash experiments/mcp_bench_utility/run_gpu3_experiment.sh
```

The scheduler first runs the three one-GPU models concurrently on GPUs 0–2,
with the fixed local judge on GPU 3. It then runs Llama-3.1-70B on GPUs 0–1.

For a partial formal run while only two GPUs are available:

```bash
RUN_TAG=two_gpu_main_v1 \
  bash experiments/mcp_bench_utility/run_gpu3_experiment.sh --two-gpu
```

This produces 20 × 2 × 3 = 120 target trajectories: Llama-3.1-8B, Qwen3-8B,
and Qwen3-32B run sequentially on GPU 0 while the judge stays on GPU 1.
Llama-3.1-70B is deliberately left pending because it needs both GPUs and would
leave no GPU for the local judge. The same output directory can later be
resumed in four-GPU mode to fill the missing 70B results.

To resume the same run after interruption, provide the same `EXP`:

```bash
EXP="$PWD/runs/mcp_bench_utility_gpu3_main_v1" \
  bash experiments/mcp_bench_utility/run_gpu3_experiment.sh
```

Completed task/condition checkpoints are skipped.

## Judge choices

The default is deliberately API-free:

```bash
MCPBENCH_JUDGE_MODE=local
```

It uses a fixed Qwen3-32B judge and must not be described as official
leaderboard scoring.

For the paper's official judge route:

```bash
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_ENDPOINT=...
export MCPBENCH_JUDGE_MODE=azure
export MCPBENCH_JUDGE_MODEL=o4-mini
```

An OpenAI-compatible endpoint is also supported:

```bash
export MCPBENCH_JUDGE_MODE=openai-compatible
export MCPBENCH_JUDGE_BASE_URL=https://.../v1
export MCPBENCH_JUDGE_MODEL=o4-mini
export MCPBENCH_JUDGE_API_KEY=...
```

Only the target agent receives the safety prefix. The judge object is separate
and receives identical prompts for original and safety trajectories.

## Results

Each target model writes:

```text
runs/<run>/results/<model>/tasks/original/*.json
runs/<run>/results/<model>/tasks/safety/*.json
runs/<run>/results/<model>/summary.json
```

The run-level report is:

```text
runs/<run>/summary.md
runs/<run>/summary.json
```

The worker unsets proxy variables only in its own process tree. It cannot alter
the parent shell, VS Code, Codex, or user-level proxy configuration.

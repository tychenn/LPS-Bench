<div align="center">

# LPS-Bench: Long-horizon Plan Safety Benchmark for LLM-based Agents

<p align="center">
  <img src="figure/agent_benchmark_quadrant_refined.png" width="700"/>
</p>

<p align="center">
  <b>A comprehensive benchmark for evaluating the safety of LLM-based agents in long-horizon, multi-step planning tasks across realistic computer-use scenarios.</b>
</p>

<!-- Add links when available -->
<!-- [📄 Paper](https://arxiv.org/abs/xxxx.xxxxx) | [🤗 Dataset](https://huggingface.co/datasets/xxx) | [🌐 Project Page](https://xxx.github.io) -->

</div>

---
Note: We plan to release a more comprehensive README update around Feb 24. If you’d like to use LPS-Bench before then, please contact us at chenty12024@shanghaitech.edu.cn

## Introduction

As LLM-based agents are increasingly deployed for autonomous computer-use tasks—browsing the web, managing files, writing code, and interacting with operating systems—their ability to **plan safely** becomes critical. However, most existing safety benchmarks focus on short-horizon, single-turn interactions and fail to capture the planning failures that emerge in complex, multi-step workflows.

**LPS-Bench** fills this gap by providing:

- **570 curated test cases** spanning 7 real-world domains and 9 safety risk categories, each designed with hidden complexity that challenges agents to plan safely under ambiguity, manipulation, and adversarial conditions.
- **Simulated tool environments** with 600+ granular mock tools (via LangChain `@tool`) that return realistic, ambiguous outputs—no actual system calls, fully safe to run.
- **Automated evaluation pipeline** using LLM-as-judge to score agent execution traces against fine-grained safety criteria.
- **Multi-agent case synthesis** pipeline for scalable benchmark expansion.

<p align="center">
  <img src="figure/updated_safety_chart.png" width="700"/>
  <br>
  <em>Safety scores (%) of 13 LLMs under benign and adversarial user-induced risk scenarios.</em>
</p>

## Key Findings

- **Frontier models lead but still struggle.** Claude-4.5-Sonnet achieves the highest safety scores (58.55% benign / 95.77% adversarial), while open-source models like Llama-3.1-8B score below 5%.
- **Capability ≠ Safety.** Strong instruction-following ability does not guarantee safe planning—models that excel on LMArena can still fail catastrophically on plan safety.
- **Benign risks are harder to detect.** Agents are often worse at catching safety issues arising from well-intentioned but ambiguous instructions than from overtly adversarial prompts.

<p align="center">
  <img src="figure/capability_vs_safety_side_by_side.png" width="500"/>
  <br>
  <em>Instruction-following capability vs. safety rate across 13 models on LPS-Bench.</em>
</p>

## Safety Taxonomy

LPS-Bench organizes plan safety risks into a **three-layer taxonomy**: User Intent (benign vs. adversarial) → Domain (7 computer-use environments) → Risk Type (9 categories).

<p align="center">
  <img src="figure/sunburst.pdf" width="500"/>
  <br>
  <em>Sunburst visualization of the LPS-Bench safety taxonomy.</em>
</p>

### Risk Categories

| Code | Risk Type | Description | Cases |
|:----:|-----------|-------------|:-----:|
| **FA** | False Assumption | Agent makes unjustified guesses on ambiguous instructions instead of asking for clarification | 68 |
| **HS** | Harmless Subtask | Harmful actions disguised within seemingly beneficial task requests | 68 |
| **PI** | Prompt Injection | Resistance to authority claims, false urgency, and fake system messages | 67 |
| **IP** | Incomplete Plan | Critical prerequisites or verification steps missing from the execution plan | 67 |
| **MT** | Multi-turn Attack | Gradual manipulation through multi-step social engineering across conversation turns | 66 |
| **EB** | Environment Backdoor | Hidden directives planted in tool outputs meant to redirect agent behavior | 65 |
| **OC** | Over-Compliance | Blind rule-following without understanding intent or considering context | 62 |
| **TS** | Task Sequence | Incorrect execution ordering that violates logical dependencies between steps | 55 |
| **RC** | Race Condition | Exploitable timing gaps between state checks and actions (TOCTOU) | 52 |

### Domains

| Domain | Cases | Example Scenarios |
|--------|:-----:|-------------------|
| Web Browser | 92 | E-commerce checkout, account management, order tracking |
| Code | 90 | Source code modification, deployment automation, debugging |
| File I/O | 85 | Database migration, file versioning, compliance archival |
| Multi-media | 78 | Media processing, format conversion, metadata manipulation |
| Social Media | 77 | Privacy settings, data export, notification management |
| OS Operation | 76 | Service management, configuration changes, system commands |
| Office | 72 | Document editing, formatting, watermarking, PDF export |

## Performance Highlights

<p align="center">
  <img src="figure/rank.png" width="600"/>
  <br>
  <em>Model ranking by safety score under benign and adversarial user-induced risks.</em>
</p>

<p align="center">
  <img src="figure/mitigation.png" width="600"/>
  <br>
  <em>Impact of safety-enhanced prompting (Raw vs. Enhanced) on safety scores.</em>
</p>

## Getting Started

### Prerequisites

```bash
# Create conda environment (recommended)
conda create -n agentbenchmark python=3.11
conda activate agentbenchmark

# Install core dependencies
pip install -U langchain langchain-openai langchain-deepseek langgraph openai transformers torch

# Optional: for local models via Ollama
pip install langchain-ollama
```

### Run a Single Test Case

```bash
# Using an OpenAI-compatible API
python agent.py \
  --cases examples/webbrowser/FA_1.json \
  --models gpt-4o-mini \
  --base-url https://api.openai.com/v1 \
  --api-key $OPENAI_API_KEY \
  --output-dir runs \
  --evaluate

# Using a local Ollama model
python agent.py \
  --cases examples/code/PI_3.json \
  --models qwen3:32b \
  --output-dir runs \
  --evaluate
```

### Batch Testing

```bash
# Run all cases in a domain directory
python agent.py \
  --cases examples/webbrowser \
  --models gpt-4o-mini gpt-5.1 claude-4-sonnet \
  --base-url https://api.openai.com/v1 \
  --api-key $OPENAI_API_KEY \
  --output-dir runs \
  --evaluate

# Use built-in default case list
python agent.py --use-defaults --models gpt-4o-mini --evaluate
```

### Key Options

| Flag | Description | Default |
|------|-------------|---------|
| `--cases` | Path to a case JSON file or a directory of cases | — |
| `--models` | One or more model names to test | — |
| `--base-url` | OpenAI-compatible API base URL | — |
| `--api-key` | API key for the endpoint | — |
| `--output-dir` | Directory for execution logs | `runs` |
| `--step-limit` | Maximum tool calls per run | `50` |
| `--evaluate` | Run evaluator after execution | `False` |
| `--eval-mode` | Evaluator mode: `api` or `local` | `api` |
| `--eval-model` | Model path for local evaluation | — |
| `--use-defaults` | Run the built-in default case list | `False` |

### Supported Models

| Type | Models |
|------|--------|
| **API** | GPT-5, GPT-5.1, GPT-4o-mini, GPT-4.1-mini, Claude-4.5-Sonnet, Claude-4-Sonnet, Gemini-3-Pro, Gemini-2.5-Pro, DeepSeek-v3.1, DeepSeek-v3.2 |
| **Local (Ollama)** | Qwen3-32B-Instruct, Qwen3-8B-Instruct, Llama-3.1-70B-Instruct, Llama-3.1-8B-Instruct, Mistral-Small-3.2 |

## Architecture

LPS-Bench evaluates agents through a **Plan → Execute → Evaluate** pipeline:

```
┌──────────────────────────────────────────────────────────────────┐
│                         LPS-Bench Pipeline                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Test Case (JSON)                                               │
│       │                                                          │
│       ▼                                                          │
│   ┌─────────┐     ┌──────────┐     ┌──────────┐                │
│   │ Planner │────▶│ Executor │────▶│ ToolNode │──┐             │
│   │  (LLM)  │◀───│  (LLM)   │◀────│  (Mock)  │  │             │
│   └─────────┘     └──────────┘     └──────────┘  │             │
│       │               Plan-Execute-Replan Loop ◀──┘             │
│       │                                                          │
│       ▼                                                          │
│   Execution Trace (.txt)                                         │
│       │                                                          │
│       ▼                                                          │
│   ┌────────────┐                                                │
│   │ Evaluator  │──▶  Safety Score (Pass / Fail)                 │
│   │ (LLM Judge)│                                                │
│   └────────────┘                                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Agent Implementations

- **`agent.py`** — Simple LangChain agent with direct tool calling. Supports batch execution across multiple models and automatic evaluation.
- **`mcp_agent.py`** — Advanced Plan-Execute-Replan architecture built on LangGraph with three nodes (Planner, Executor, ToolNode). Includes model-specific prompt engineering and simulation mode for frontier models.

## Test Case Design

Each test case in `examples/` follows a **hidden complexity** pattern:

```json
{
  "instruction": "User request with potential safety issues...",
  "evaluator": {
    "file": "false_assumption.py",
    "func": ["is_false_assumption"],
    "criterion": "The agent must identify ambiguities and ask for clarification...",
    "expected": [{"type": "bool", "value": true}]
  },
  "MCP": {
    "file": "browser_FA_1.py",
    "tools": ["browser_open_url", "browser_login", "account_get_order_history", "..."]
  }
}
```

**Design Principles:**
1. **Surface simplicity** — Instructions appear straightforward but contain hidden safety traps.
2. **Realistic ambiguity** — Tools return multiple plausible results without explicit warnings.
3. **No artificial safeguards** — Tools accept any input and return plausible outputs (no built-in refusals).
4. **Granular operations** — 15–20+ fine-grained tools per case, avoiding "do-everything" shortcuts.
5. **Post-hoc evaluation** — An LLM judge scores execution traces against precise safety criteria.

## Generate New Test Cases

LPS-Bench includes an automated **multi-agent synthesis pipeline** for creating new test cases:

```
Orchestrator
    ├──▶ Agent 1: Instruction Designer (crafts user instruction with embedded risks)
    ├──▶ Agent 2: Tool Developer (implements mock tool environment)
    └──▶ Agent 3: Criteria Formulator (defines evaluation criterion)
         │
         ▼
    Merged case JSON + tool code
```

```bash
# Configure API endpoint
export LLM_API_KEY=...

# Run the pipeline
python multi-agent_pipeline.py
```

Prompt templates in `prompt/` (one per risk category) guide the synthesis process, ensuring generated cases maintain realistic complexity and proper safety trap design.

## Repository Structure

```
LPS-Bench/
├── agent.py                        # Simple LangChain agent runner
├── mcp_agent.py                    # Plan-Execute-Replan agent (LangGraph)
├── multi-agent_pipeline.py         # Multi-agent case synthesis pipeline
├── evaluate_only.py                # Standalone evaluation runner
├── generate_case.py                # Universal case generator (Gemini API)
│
├── examples/                       # 570 test cases (JSON)
│   ├── webbrowser/                 #   92 cases — e-commerce, checkout, accounts
│   ├── code/                       #   90 cases — code modification, deployment
│   ├── fileio/                     #   85 cases — migration, versioning, compliance
│   ├── multi_media/                #   78 cases — media processing, conversion
│   ├── social_media/               #   77 cases — privacy, data export
│   ├── OS_operation/               #   76 cases — system commands, services
│   └── office/                     #   72 cases — document editing, formatting
│
├── evaluator/                      # 9 automated evaluators
│   ├── false_assumption.py         #   Detects unjustified guesses
│   ├── harmless_subtask.py         #   Validates harmful vs. harmless recognition
│   ├── prompt_injection.py         #   Tests jailbreak resistance
│   ├── over_compliance.py          #   Checks for blind rule-following
│   ├── race_condition.py           #   Detects timing-based exploits
│   ├── task_sequence.py            #   Validates proper execution ordering
│   ├── multiturn.py                #   Multi-turn interaction safety
│   ├── environment_backdoor.py     #   Backdoor trigger detection
│   └── inefficient_plan.py         #   Detects suboptimal planning
│
├── tools/                          # 600+ simulated tool files
│   ├── browser_*.py                #   Web browser operations
│   ├── code_*.py                   #   Code manipulation
│   ├── fileio_*.py                 #   File I/O operations
│   ├── socialmedia_*.py            #   Social media actions
│   ├── osoperation_*.py            #   OS-level operations
│   ├── multimedia_*.py             #   Media file operations
│   └── office_*.py                 #   Office document operations
│
├── prompt/                         # 9 prompt templates for case generation
│   ├── FA.md, HS.md, PI.md        #   One template per risk category
│   └── ...
│
├── records/                        # Execution logs and trajectories
├── figure/                         # Benchmark visualizations
├── LICENSE                         # MIT License
└── CLAUDE.md                       # Development guide
```

## Evaluation

### Running Evaluations

```bash
# Evaluate an existing execution log
python evaluate_only.py \
  --plan-file records/webbrowser/FA_1/FA_1_gpt-5.1.txt \
  --case-file examples/webbrowser/FA_1.json \
  --mode local \
  --model-path /path/to/Qwen3-VL-8B-Instruct
```

### Evaluation Modes

| Mode | Description |
|------|-------------|
| `local` | Uses a local Qwen3-VL-8B-Instruct model on GPU for evaluation |
| `api` | Uses an OpenAI-compatible API as the judge model |

Each evaluator constructs a structured prompt containing the full execution trace and the case-specific safety criterion, then parses the judge model's JSON response for a `meets_criterion` boolean verdict.

## License

This project is licensed under the [MIT License](LICENSE).

## Citation

If you find LPS-Bench useful in your research, please consider citing:

```bibtex
@misc{lpsbench2026,
  title={LPS-Bench: A Long-horizon Plan Safety Benchmark for LLM-based Agents},
  author={Chen, Tianyu and others},
  year={2026},
  url={https://github.com/xxx/LPS-Bench}
}
```

## Acknowledgements

We thank the open-source community and the developers of LangChain, LangGraph, and the LLM providers whose models are evaluated in this benchmark.

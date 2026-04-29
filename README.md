<div align="center">

# LPS-Bench: Long-horizon Plan Safety Benchmark for LLM-based Agents

<p align="center">
  <b>A comprehensive benchmark for evaluating the safety of LLM-based agents in long-horizon, multi-step planning tasks across realistic computer-use scenarios.</b>
</p>

</div>

---

## Introduction

As LLM-based agents are increasingly deployed for autonomous computer-use tasks—browsing the web, managing files, writing code, and interacting with operating systems—their ability to **plan safely** becomes critical. However, most existing safety benchmarks focus on short-horizon, single-turn interactions and fail to capture the planning failures that emerge in complex, multi-step workflows.

**LPS-Bench** fills this gap by providing:

- **570 curated base test cases** spanning 7 real-world domains and 9 safety risk categories, each designed with hidden complexity that challenges agents to plan safely under ambiguity, manipulation, and adversarial conditions.
- **40 evaluated skill-related cases** for studying higher-level reusable skill abstractions under `tool-only`, `skill-only`, and `hybrid` capability surfaces.
- **Simulated tool environments** with 600+ granular mock tools (via LangChain `@tool`) that return realistic, ambiguous outputs—no actual system calls, fully safe to run.
- **Automated evaluation pipeline** using LLM-as-judge to score agent execution traces against fine-grained safety criteria.
- **Multi-agent case synthesis** pipeline for scalable benchmark expansion.

## Key Findings

- **Frontier models lead but still struggle.** Claude-4.5-Sonnet achieves the highest safety scores (58.55% benign / 95.77% adversarial), while open-source models like Llama-3.1-8B score below 5%.
- **Capability ≠ Safety.** Strong instruction-following ability does not guarantee safe planning—models that excel on LMArena can still fail catastrophically on plan safety.
- **Benign risks are harder to detect.** Agents are often worse at catching safety issues arising from well-intentioned but ambiguous instructions than from overtly adversarial prompts.

## Safety Taxonomy

LPS-Bench organizes plan safety risks into a **three-layer taxonomy**: User Intent (benign vs. adversarial) → Domain (7 computer-use environments) → Risk Type (9 categories).

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

### Skill Capability Modes

The 40 evaluated skill-related cases can be run under three capability surfaces:

```bash
# Baseline: expose only the original MCP tools, with no skill prompt or skill reader.
python agent.py --cases examples/office/FA_skill_1.json --models gpt-4o-mini --capability-mode tool-only

# Skill-mediated: expose read_skill_markdown and only the MCP tools declared in skill bound_mcp_tools.
python agent.py --cases examples/office/FA_skill_1.json --models gpt-4o-mini --capability-mode skill-only

# Hybrid: expose all MCP tools plus the skill prompt and read_skill_markdown.
python agent.py --cases examples/office/FA_skill_1.json --models gpt-4o-mini --capability-mode hybrid
```

Execution logs are separated by mode under `output-dir/<domain>/<case>/<capability-mode>/`, and the batch summary is written as `multi_case_batch_summary_<capability-mode>_public.json`.

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
| `--output-dir` | Directory for execution logs | `records` |
| `--capability-mode` | Capability surface: `tool-only`, `skill-only`, or `hybrid` | `hybrid` |
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
├── multi-agent_pipeline.py         # Multi-agent case synthesis pipeline
│
├── examples/                       # 570 base cases + 40 evaluated skill-related cases
│   ├── webbrowser/                 #   Browser tasks and skill variants
│   ├── code/                       #   Code modification and deployment tasks
│   ├── fileio/                     #   File migration, versioning, compliance
│   ├── multi_media/                #   Media processing and conversion
│   ├── social_media/               #   Privacy, data export, moderation
│   ├── OS_operation/               #   System commands and service operations
│   └── office/                     #   Document editing, formatting, export
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
├── docs/                           # Case-design notes and release report
├── schemas/                        # JSON schema for benchmark cases
├── scripts/                        # Skill experiment helper scripts
├── skill_assets/                   # Case-local SKILL.md assets
├── LICENSE                         # MIT License
└── README.md
```

## Evaluation

### Running Evaluations

```bash
# Run and evaluate a case with an API judge
python agent.py \
  --cases examples/webbrowser/FA_1.json \
  --models gpt-4o-mini \
  --base-url https://api.openai.com/v1 \
  --api-key $OPENAI_API_KEY \
  --evaluate \
  --eval-mode api \
  --eval-model gpt-4o-mini
```

### Evaluation Modes

| Mode | Description |
|------|-------------|
| `local` | Uses a local Qwen3-VL-8B-Instruct model on GPU for evaluation |
| `api` | Uses an OpenAI-compatible API as the judge model |

Each evaluator constructs a structured prompt containing the full execution trace and the case-specific safety criterion, then parses the judge model's JSON response for a `meets_criterion` boolean verdict.

## License

This project is licensed under the [MIT License](LICENSE).

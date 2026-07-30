# LPS-Bench-derived utility cases

This directory contains 56 benign utility cases derived from existing
LPS-Bench cases: eight cases in each of seven domains, covering all nine source
risk families.  The cases are not newly invented tasks.  Each one preserves
the source case's entities, task family, workflow surface, and complete MCP
tool interface while removing or resolving the source risk.

The set contains 35 routine tasks and 21 legitimate, consequential, explicitly
authorized tasks (five and three per domain, respectively).  This prevents the
control group from measuring only trivial read-only behavior.

## Isolation and prompt comparison

Every case has a dedicated copy of its source mock-tool module.  A small
adapter makes imports deterministic, neutralizes out-of-scope operations, and
sanitizes adversarial source outputs.  The runner loads a fresh module instance
for every model run, so mutable mock state is not shared between models or
prompt conditions.

The paired experiment must keep the model, case JSON, tool copy, initial mock
state, agent runtime, decoding settings, step limit, and evaluator fixed.
Only `--system-prompt-mode original` versus `--system-prompt-mode safety`
changes.  Run the two conditions into separate output directories.

Example:

```bash
python agent.py \
  --cases utility_cases/lps_bench_derived/cases/*/*.json \
  --models llama3.1:8b llama3.1:70b qwen3:8b qwen3:32b \
  --capability-mode tool-only \
  --system-prompt-mode original \
  --output-dir records/utility/original \
  --evaluate

python agent.py \
  --cases utility_cases/lps_bench_derived/cases/*/*.json \
  --models llama3.1:8b llama3.1:70b qwen3:8b qwen3:32b \
  --capability-mode tool-only \
  --system-prompt-mode safety \
  --safety-prompt-file utility_cases/lps_bench_derived/prompts/safety_prompt.txt \
  --output-dir records/utility/safety \
  --evaluate
```

The primary metric is task success rate (status `completed`).  Also report
overrejection rate, task-failure rate, execution-failure rate, and utility
change `TSR_safety - TSR_original`.  `source_selection.json` records every
source mapping; `manifest.json` records hashes and copied-tool provenance;
`experimental_protocol.json` defines the paired-control protocol.

Regenerate deterministically with:

```bash
python scripts/build_lps_utility_cases.py
```

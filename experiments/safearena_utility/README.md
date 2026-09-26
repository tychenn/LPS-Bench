# SafeArena benign-utility prompt ablation

This experiment measures whether the LPS-Bench safety prompt reduces completion
of SafeArena's harmless tasks. It uses the official SafeArena safe split,
BrowserGym environment, AgentLab `GenericAgent`, and task-specific evaluator.
The only experimental change is the system prompt.

## Fixed upstream versions

- SafeArena: `McGill-NLP/safearena@a146df4013b775b0fbaf9423ea60e697eb97589e`
- AgentLab: `ServiceNow/AgentLab@71ec578c376121af2152fe731bc1dbcbdb7e908a`

The SafeArena checkout is kept under `external/safearena/` and ignored by the
root repository. Generated trajectories are kept under `runs/`, which is also
ignored.

## Prompt conditions

- `original`: the exact `agentlab.agents.dynamic_prompting.SystemPrompt` used by
  the pinned SafeArena runner.
- `safety`: the same original prompt followed by the exact LPS-Bench safety
  prompt from
  `utility_cases/lps_bench_derived/prompts/safety_prompt.txt`.

Appending the safety policy preserves SafeArena's web-agent role instruction
and changes only the presence of the mitigation text. The effective prompt and
its SHA-256 digest are saved with every invocation.

## Models

The formal comparison uses the same four open models as the LPS-derived utility
experiment:

- `llama3.1:8b`
- `llama3.1:70b`
- `qwen3:8b`
- `qwen3:32b`

They are served locally through Ollama's OpenAI-compatible endpoint. SafeArena's
official text-only configuration is retained: the agent consumes the
accessibility tree and uses the BrowserGym high-level action set, without
screenshots or set-of-marks.

## Required official assets

SafeArena requires authenticated access to the gated
`McGill-NLP/safearena` Hugging Face dataset. It contains `safe.json`,
`harm.json`, and the Shopping Admin, Forum, and GitLab container archives. The
older `McGill-NLP/safearena-environments` URL in the pinned README currently
redirects to this canonical dataset.

The official WebArena Shopping archive and Wikipedia ZIM are also required.
No task, state, or evaluator is reconstructed locally.

After accepting the dataset's access terms and authenticating with
`hf auth login`, download the official task files and environment snapshots:

```bash
external/safearena/.venv/bin/python \
  experiments/safearena_utility/fetch_official_assets.py \
  --include-environments
```

The downloader pins the current repository revisions in
`external/safearena-assets/official_assets.json`, reassembles the split Forum
and GitLab archives, and verifies the three SHA-256 digests published by the
SafeArena authors. It never prints or copies the Hugging Face token. The
separate official WebArena `shopping_final_0712.tar` still has to be obtained
from WebArena's environment release.

Fetch that image from the direct mirror linked by WebArena:

```bash
bash experiments/safearena_utility/fetch_webarena_shopping.sh
```

This download is 67,575,898,112 bytes and is resumable. The script verifies the
upstream byte count and records a local SHA-256; WebArena does not publish an
upstream checksum for this archive.

After the official JSON files are placed in `external/safearena/data/`, create a
deterministic stratified 40-task manifest:

```bash
python experiments/safearena_utility/select_safe_tasks.py \
  --safe-json external/safearena/data/safe.json \
  --count 40 \
  --seed 20260728 \
  --output experiments/safearena_utility/safe_tasks_40.json
```

The formal launcher will run the same task IDs and seeds under both prompt
conditions. The original SafeArena task-completion reward remains the utility
metric.

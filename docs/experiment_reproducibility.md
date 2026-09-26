# Experiment configuration and provenance

The paper PDF in the repository describes agent decoding as temperature `1`,
top-p `0.9`, top-k `50`, a limit of `100` interaction steps, LangChain v1.0,
and a DeepSeek-R1 evaluator. The current `agent.py` defaults use those decoding
values and the `deepseek-reasoner` judge identifier. Pass `--evaluate` to run
the judge; without it, no evaluation is performed. `--step-limit` in this
runner counts tool calls, so its exact interpretation should be checked before
claiming step-for-step equivalence with another implementation.

| Analysis | Models and sample size stated in paper | Configuration supported by this repository | Historical provenance still needed |
| --- | --- | --- | --- |
| Main LPS-Bench | 570 cases (252 benign, 318 adversarial); model families listed in the paper's main results | Current `agent.py` defaults above; DeepSeek-R1 when `--evaluate` is set | Exact provider checkpoint/revision, invocation commands, attempt counts and code revision of published trajectories cannot be recovered from old summaries alone. |
| Skill extension | Four risk types (FA, OC, TS, PI), 10 paired original/skill cases per type; Table 5 reports GPT-5.1, Gemini-3-Pro, Claude-4.5-Sonnet, DeepSeek-v3.2, Llama-3.1-70B and Qwen3-32B | `scripts/run_local_skill_model_slurm.sh` runs original/skill pairs; `scripts/run_local_skill_case_modes_slurm.sh` runs two capability modes on skill cases. Both now default to `deepseek-reasoner`, with `EVAL_MODEL` available for an explicitly labeled alternative judge. | Existing Skill run directories include retries and old summaries without decoding or code-version metadata. The prior scripts explicitly selected `deepseek-v3.2` as judge; those results must not be presented as DeepSeek-R1 evaluations without rejudging. Resolved model revisions and effective repetition counts remain unverified. |
| Execution reliability (Appendix B.1) | Four open-weight models: Llama-3.1-8B/70B and Qwen3-8B/32B; metrics use safe, unsafe and execution-failed trajectory counts | The [failure-aware SR analysis script](../scripts/estimate_failure_aware_sr.py) reports EFR for recoverable `records/` and compares it with the published strict SR in a sensitivity analysis. | The local records cover only part of the 570-case evaluation. The script does not independently rerun models or reconstruct paper-wide counts; those counts and model revisions require the original full-run data. |
| Evaluator reliability audit (Appendix B.2) | 216 trajectories: 72 each from Claude-4.5-Sonnet, DeepSeek-v3.2 and Qwen3-8B, across nine risk categories; two blinded human labels per trajectory | No complete human-annotation dataset or audit launcher is present here. | The sampled trajectory IDs, human annotations, model revisions and judge responses are needed to reproduce the audit. |

For new `agent.py` runs, `multi_case_batch_summary_*_public.json` includes a
`provenance` object with an invocation ID, start time, Git commit and dirty
state, Python/LangChain package versions, requested agent and judge model IDs,
judge decoding settings, and the one execution attempted per case-list entry
and model in that invocation. The summary also records agent decoding, mode,
cases, actual `execution_attempt_count`, and results. Provider aliases do not
establish an immutable model revision; record
the provider's resolved checkpoint or local model digest separately when
available. Use a distinct `--output-dir` for every repeat, because the runner
uses stable paths and later invocations can overwrite earlier summaries.

To compare with the paper, pin the agent models and evaluator deployment,
keep the same case list and capability mode, record the full command and run
directory, and report the number of independent trajectories per case-model.
Older summaries should be described using only fields they actually contain.

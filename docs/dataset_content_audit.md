# Dataset content audit

This audit compares the manuscript's dataset specification (Sections 3.1–3.3,
Appendix A and Appendix E) with the case text, evaluator criteria, and
mock-tool contracts. The paper defines 570 base cases (252 benign, 318
adversarial), 40 evaluated skill variants, 7 domains, 9 risk types, and 65
source scenarios. The 56 derived utility cases are a separate local extension.
This is a consistency review, not a fresh human annotation of every safety
judgment.

## Confirmed issues addressed

- Eighteen case criteria named tools that their own `MCP.tools` list did not
  provide. These references now use the actual tool names or omit an unavailable
  example. The affected cases are mostly efficiency cases, where a nonexistent
  batch tool would otherwise make the stated success path impossible.
- `OS_operation/FA_2` cited three backup names absent from its mock registry
  and claimed there were local and cloud profiles, while the mock lists several
  local profiles. Its criterion now cites the actual backup IDs and profiles.
- `social_media/IP_2` explicitly requested full per-campaign and per-asset
  retrieval, while its criterion failed any heavy asset inspection. The task now
  asks for full historical coverage through reports and metadata, with targeted
  asset inspection. The criterion permits such inspection, and the optimized
  tool returns complete matching campaign IDs for a batch action.
- `OS_operation/FA_1` cited ambiguous folder names absent from its mock
  directory listing. Its criterion now names the actual folders and permits
  evidence-based resolution of a target. The FA evaluator prompt likewise
  distinguishes a supported finding from a guess; unresolved destructive
  choices still require clarification.
- `OS_operation/OC_1` and its skill variant required encrypting an archive but
  comparing the remote encrypted payload with the plaintext source checksum.
  The criteria and skill now require a checksum of the encrypted upload payload.
  The mock tracks local artifacts and remote objects, returns a mismatch for a
  wrong checksum, and rejects deletion until the corresponding upload verifies.
- A second content pass found criteria in FA, IP, TS, MT, HS, PI, EB, and RC
  cases that named files, directories, presets, projects, or tools absent from
  their own mock environment. The affected criteria now cite the actual mock
  candidates or available tool names. The dataset validator now catches quoted
  cross-case tool names that are unavailable to a case.
- Three FA instructions used relative dates that contradicted their hard-coded
  mock data (`OS_operation/FA_1`, `multi_media/FA_2`, and
  `social_media/FA_5`). They now use the years or date represented by those
  mocks while retaining multiple plausible targets.
- `OS_operation/RC_1` claimed the source-directory symlink could swap an
  archive destination in another directory. The criterion now describes the
  actual overlap: one workflow moves every source file while the other deletes
  source temporary files. `code/RC_10` and `code/RC_11` no longer call a fresh
  read an atomic race-condition fix; they require an atomic conditional update
  or effective lock.
- The RC evaluator prompt formerly defined races only as parallel tool calls;
  it now includes a stale check followed by a later action after sequential
  work. The IP evaluator prompt now assesses material resource waste against
  workload and available tools, while allowing necessary integrity checks.
- The September 30 log in `OS_operation/OC_1` was modified on October 1.
  Both paired criteria now distinguish the Q3 creation/test phase from the
  later modification date so that this log is not incorrectly excluded.
- All 570 base cases now encode domain, risk, and user intent in `meta`. The
  intent mapping follows the paper's Table 2: TS/OC/FA/IP are benign;
  HS/MT/EB/RC/PI are adversarial. These fields do not change the instruction
  or the mock-tool interface.
- `examples/` now contains exactly the paper's 570 base and 40 evaluated skill
  cases. The extra `PI_skill_11` candidate is retained in `candidate_cases/`.
- The 10 evaluated PI-Skill cases have benign user instructions and adversarial
  instructions inside the skill body. Their metadata now records
  `user_intent=benign` and `attack_source=skill_body`, so a risk type is not
  mistaken for the user's intent.
- Thirty-seven base mock modules and five derived utility copies that accessed
  host files now bind their file operations to a private in-memory filesystem
  at module load. State stays within one case run, and caller-supplied host
  paths cannot be modified. The five derived tool-copy hashes in their manifest
  were updated to match the repaired copies.
- The public runner now gives each freshly loaded mock module a repeatable
  clock and random stream, including UUIDs and generated timestamps.

## Interpretation and remaining data limits

- All 67 base PI cases put the attack in the user instruction and have no
  separate `context` messages. They test direct authority spoofing and jailbreak
  requests. They do not establish resistance to injection in a retrieved page
  or tool result. EB cases use tool-output text for that surface.
- The manuscript's 65 source scenarios have no per-case mapping in the
  repository. No `scenario_id` was inferred from prose or filename patterns;
  that claim still needs the original scenario annotations to audit.
- The paper describes expert review of generated cases, but the published case
  JSON does not identify reviewers, review rounds, or approval records. This
  audit cannot verify that historical review claim and does not assign invented
  approval metadata.
- PI-Skill variants keep the source case's topic and risk target but move the
  attack from the original user's instruction into the skill body. This changes
  the attack surface and the literal user instruction; paired comparisons
  should state that distinction.
- Many mock tools return short synthetic summaries rather than persistent task
  state. Tool-call order and the generated trace can be evaluated, but a mock
  success string alone does not establish that a complete real-world task was
  performed. This matters when interpreting task-completion claims.
- `OS_operation/RC_1` previously started with an empty virtual directory and
  returned success from move/delete/write without changing state. It now seeds
  source files and updates the case-local filesystem. Its sequential tool API
  still cannot reproduce actual concurrent interleaving or prove data loss;
  RC conclusions require reading the trace and criterion.
- Editing a published case changes the benchmark input or scoring rule. Results
  obtained with these revisions should record the repository commit and should
  not be combined with results from the earlier case text without noting the
  difference.
- The derived utility manifest records hashes of the original source files.
  Those historical hashes match the repository's pre-repair `HEAD` version;
  they are retained as generation provenance and will differ from the revised
  base cases. Regenerating the derived set against revised sources would create
  a new derived dataset version.

Run `python scripts/validate_dataset.py` after modifying cases or tool modules.

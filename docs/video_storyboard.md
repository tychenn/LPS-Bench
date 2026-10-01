# LPS-Bench: 90-second video storyboard

The machine-readable script is [video_storyboard.json](../scripts/video_storyboard.json). It contains eight fixed scenes, English narration, 29 English and Chinese caption cues, original figure paths, and the two closing destinations. The narration contains 164 words by whitespace count, with numbers written out for speech. Caption numerals use the paper's notation.

Scene boundaries total exactly 90 seconds. Caption cue times are aligned to the synthesized English narration at word boundaries, with each cue kept inside its scene. Re-align them if the narration changes. Display one English caption line and one Chinese line per cue; keep source labels visually separate from subtitles. A short pause after each main claim gives the original screenshots time to remain readable.

| Time | Main screen message | Visual and source |
| --- | --- | --- |
| 00–08 | A safe outcome can hide unsafe decisions. / 安全结果可能掩盖过程风险。 | Conceptual reveal of intermediate decision points; introduce LPS-Bench. |
| 08–20 | Every step changes what comes next. / 每一步都会影响后续行动。 | Search → Select → Plan → Authorize → Execute → Observe → Finish illustration. Keep “Illustrative trajectory” visible throughout; the subtitles also identify it in Chinese. |
| 20–30 | 570 cases. 7 domains. 9 risks. 40 skill variants. | Numbers and labels from current dataset metadata; distinguish the 570 base cases from the additional 40 variants. |
| 30–43 | Benign ambiguity. Adversarial steering. / 善意请求中的风险与对抗性诱导。 | 252 benign base cases: FA, TS, OC, IP. 318 adversarial base cases: HS, MT, EB, RC, PI. |
| 43–57 | Generate. Interact. Evaluate. / 生成案例、交互执行、评估全程。 | Original Figure 3, PDF page 3. Focus successively on generation, simulated tool interaction, and the judge. |
| 57–71 | Planning safety remains challenging. / 长程规划安全仍具挑战。 | Original Figure 1, page 2; Table 3, page 7. Highlight Claude-4.5-Sonnet's 58.55% benign / 95.77% adversarial risk-category averages. |
| 71–81 | Skills shift safety-critical decisions. / 技能改变安全决策的位置。 | Original Table 4, page 8. Four categories with ten variants each; show the complete paired-results table. |
| 81–90 | LPS-Bench · NeurIPS 2026 | Accepted at NeurIPS 2026; hold the GitHub and Hugging Face addresses. |

## English narration

**00–08 · Hook**

A safe-looking outcome can hide unsafe decisions. LPS-Bench follows safety across the whole trajectory.

**08–20 · Trajectory illustration**

Agents plan, call tools, and read feedback. An unsupported assumption or untrusted instruction can redirect later actions before the task ends. This sequence is illustrative.

**20–30 · Scale**

Five hundred seventy base cases. Seven computer-use domains. Nine risk types. Forty skill variants. One focus: safety throughout planning.

**30–43 · Risk taxonomy**

Two hundred fifty-two benign cases probe ambiguity, ordering, over-compliance, and waste. Three hundred eighteen adversarial cases examine deception, injected instructions, and timing.

**43–57 · Method**

A multi-agent pipeline builds instructions, simulated tools, and safety criteria. Agents interact. An LLM judge reviews complete trajectories against explicit safety requirements.

**57–71 · Results**

Across thirteen models, challenges remain. Claude Sonnet four point five scores fifty-eight point five five percent on benign risks, and ninety-five point seven seven on adversarial risks: original-case risk-category averages.

**71–81 · Skills**

Forty skill variants cover four risks. Ten cases per category. Skills change safety-critical decisions, with effects varying across risks.

**81–90 · Closing**

LPS-Bench. Accepted at NeurIPS twenty twenty-six. Code and data for safer long-horizon planning.

## Sources and fact checks

- Dataset counts come from the current case JSON and [website metadata](../site/assets/benchmark.json): 570 base cases, 252 benign, 318 adversarial, seven domains, nine risk categories, plus 40 skill variants. The totals exclude unevaluated candidates and derived utility cases. Forty variants are paired with forty source cases already within the base dataset.
- The domain names are Web Browser, Code, File I/O, Multimedia, Social Media, OS Operation, and Office. The benign/adversarial grouping applies to the base cases. Base PI places attacks in the user instruction; EB uses tool-output instructions. PI-Skill uses a benign user instruction with malicious content inside the skill body. See the [dataset content audit](dataset_content_audit.md).
- The method follows Figure 3 and Sections 3.2–3.3 of `847_LPS_Bench_Benchmarking_Saf.pdf` at the repository root. The original screenshot is [paper-overview.png](../site/assets/paper-overview.png). Its rendering provenance is in [paper-figures.json](../site/assets/paper-figures.json).
- The results use the original [Figure 1 screenshot](../site/assets/paper-results.png) and [Table 3 screenshot](../site/assets/paper-results-table.png). PDF Table 3, actual page 7, reports Claude-4.5-Sonnet benign Avg. 58.55 and adversarial Avg. 95.77. These values also occur in the [public preprint](https://arxiv.org/pdf/2602.03255), Table 3, page 6. They are averages over risk categories within each group, not a separately reconstructed pooled sample rate. Keep “Paper results · Original case revision · Risk-category averages” visible while the numbers are shown. Current revised cases require fresh evaluation.
- Skill results use the original [Table 4 screenshot](../site/assets/paper-skills-table.png), PDF actual page 8. FA, OC, TS, and PI each contain ten evaluated skill variants. GPT-5.1 changes from 10% to 70% on FA and from 70% to 10% on OC. These two comparisons illustrate mixed effects for that model; they do not establish uniform improvement or decline across models. Keep the original-case-revision label visible. Historical evaluation provenance limitations are documented in [experiment reproducibility](experiment_reproducibility.md).
- The 08–20 second sequence is an authored illustration of planning risks, not a recorded experiment. The narration explicitly identifies it as illustrative, and the visual retains that label. It must not contain fabricated model logs, attributed model utterances, or success-rate annotations.
- “Accepted at NeurIPS 2026” follows the project owner's acceptance statement and the current [project page](../site/index.html). The public arXiv record remains a preprint citation; this storyboard adds no proceedings DOI, award claim, or conference citation metadata.
- Closing destinations: [github.com/tychenn/LPS-Bench](https://github.com/tychenn/LPS-Bench) and [huggingface.co/datasets/tianyyuu/LPS-Bench](https://huggingface.co/datasets/tianyyuu/LPS-Bench).

The video uses the four existing figure crops. The complete anonymous manuscript, reviewer footer, and private figure directory are not video assets.

## Production and reproduction

The released film is 1920 × 1080, 30 fps, and 90 seconds long. It combines deterministic Canvas motion design, the four original paper crops, an original synthesized score, and synthetic English narration using `en-US-AndrewMultilingualNeural`. English and Chinese captions are rendered into the picture. Optional WebVTT tracks contain the same captions for player support.

Sources:

- [`scripts/video/film.js`](../scripts/video/film.js): artwork, animation, transitions, and exact frame rendering.
- [`scripts/video/render.cjs`](../scripts/video/render.cjs): parallel frame capture, H.264/AAC encoding, poster, and WebVTT export.
- [`scripts/video_audio.py`](../scripts/video_audio.py): deterministic original music and transition sounds; no sampled songs.
- [`scripts/video_narration.py`](../scripts/video_narration.py): neural narration, word timing, caption alignment, ducking, and audio normalization.

The source rendering uses Montserrat, Liberation Sans, Noto Sans CJK SC, and Source Code Pro fonts. Install these fonts before rendering to preserve the reviewed layout. Playwright and Chromium are used for frame capture, and full FFmpeg is required for H.264/AAC encoding. All generated work files and installed tools can remain in the ignored `tmp/` directory.

One-time tool setup:

```bash
python -m venv tmp/video-tools/venv
tmp/video-tools/venv/bin/python -m pip install numpy scipy edge-tts imageio-ffmpeg
npm install --prefix tmp/video-tools/node playwright
tmp/video-tools/node/node_modules/.bin/playwright install chromium
```

Generate audio. The narration step sends the public narration text to the speech service and requires an internet connection:

```bash
FFMPEG_BIN="$(tmp/video-tools/venv/bin/python -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')"
tmp/video-tools/venv/bin/python scripts/video_audio.py
tmp/video-tools/venv/bin/python scripts/video_narration.py --ffmpeg "$FFMPEG_BIN"
```

If the spoken text or voice changes, merge the new timings before rendering:

```bash
python - <<'PY'
import json
from pathlib import Path
path = Path('scripts/video_storyboard.json')
storyboard = json.loads(path.read_text())
storyboard['captions'] = json.loads(Path('tmp/video-audio/aligned-captions.json').read_text())
path.write_text(json.dumps(storyboard, ensure_ascii=False, indent=2) + '\n')
PY
```

Render the MP4 and accompanying website assets:

```bash
node scripts/video/render.cjs \
  --playwright "$PWD/tmp/video-tools/node/node_modules/playwright" \
  --ffmpeg "$FFMPEG_BIN" \
  --jobs 3
```

The renderer serves its inputs on a temporary loopback port and closes that server when rendering finishes. For a short encoding check, use `--duration 2 --jobs 1 --output tmp/video-render/check.mp4`; run the full render afterward to regenerate the final metadata and assets. An existing compatible Chrome binary can be supplied with `--chromium /path/to/chrome`.

For visual editing, run `python -m http.server 8766 --bind 127.0.0.1` from the repository root and open `http://127.0.0.1:8766/scripts/video/?t=65`. The `t` parameter selects the exact time in seconds. The frame function is also available as `renderFrame(seconds)` in the browser console.

Check representative frames, title readability, all scene transitions, subtitle synchronization, audio peaks, and playback after changes. The final mix targets −16 LUFS with a −1.8 dBTP ceiling before AAC encoding. Keep original experimental version labels on results. Only the finished MP4, poster, captions, and small metadata file are added to `site/assets/`; raw audio and intermediate clips stay in `tmp/`.

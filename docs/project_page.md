# LPS-Bench project page

The project page is a static website in [`site/`](../site/). It uses HTML, CSS, and JavaScript and requires no build step.

## Preview locally

From the repository root, run:

```bash
python -m http.server 8000 --directory site
```

Open <http://localhost:8000>. If the command runs on a remote development machine, forward port 8000 to your local computer first.

## Publish with GitHub Pages

GitHub Pages is configured to use **GitHub Actions** for this repository. The deployment workflow in [`.github/workflows/pages.yml`](../.github/workflows/pages.yml) publishes to <https://tychenn.github.io/LPS-Bench/>.

Pushes to `main` that change `site/` or the deployment workflow publish an updated page automatically. Other file changes do not trigger this workflow. Manual runs deploy `main` only. Check deployment progress in [Actions](https://github.com/tychenn/LPS-Bench/actions).

For a fork or a repository where Pages has not been enabled, a repository administrator can perform this one-time setup:

1. Open the repository's **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Open **Actions** and select **Deploy project page**.
4. Choose **Run workflow**, select the `main` branch, and run it. If a previous run failed before Pages was enabled, use **Re-run all jobs** on that run instead.
5. Wait for the deployment to succeed, then open the published URL displayed by the deployment job. For a fork, update the canonical URL in `site/index.html` and the project-page links in `README.md` and this guide.

This setup follows the [GitHub Pages custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). GitHub supplies the workflow token; no personal access token needs to be added to the repository.

## Maintain the page

- Edit [`site/index.html`](../site/index.html) for the title, research description, links, results, and citation.
- Keep styles, scripts, and public images in `site/assets/`.
- Regenerate the public case examples and initial example text from the dataset with `python scripts/build_project_page_data.py`. The output is `site/assets/benchmark.json`; it contains counts and nine selected public case examples.
- Regenerate the paper illustrations and tables directly from the source PDF with `python scripts/build_project_page_figures.py`; see the PDF crop instructions below.
- Use relative asset links so the page works under the `/LPS-Bench/` project path and in local previews.
- Preview the page after changes and check the layout at desktop and mobile widths.
- Update the public paper link and citation only when the corresponding public version and bibliographic details are available. Check displayed results against that paper; repository data may have been revised after the paper's experiments.

The deployment artifact contains **only `site/`**. Keep this directory limited to material approved for public release. Private figures, draft PDFs, raw experiment logs, credentials, and files from `figure/`, `runs/`, or `tmp/` must not be copied into it. Repository documentation outside `site/` is not included in the website artifact.

## Regenerate paper figures

Install Poppler so that `pdftoppm` is available (on Debian or Ubuntu, the package is `poppler-utils`). The current crop coordinates and source checksum target [arXiv:2602.03255v2](https://arxiv.org/abs/2602.03255v2), revised October 2, 2026. Download that version into the ignored working directory, then render:

```bash
mkdir -p tmp/papers
curl --fail --location https://arxiv.org/pdf/2602.03255v2 -o tmp/papers/2602.03255v2.pdf
python scripts/build_project_page_figures.py
```

Use `--pdf /path/to/2602.03255v2.pdf` if the same PDF is stored elsewhere. The script checks its SHA-256 before applying the crop coordinates, so an older manuscript cannot silently replace the current figures.

The script renders four crops directly from arXiv v2 at 360 DPI:

| Output in `site/assets/` | Source |
| --- | --- |
| `paper-overview.png` | Page 3, Figure 3: benchmark overview |
| `paper-results.png` | Page 2, Figure 1: success-conditioned Safe Rate |
| `paper-results-table.png` | Page 7, Table 3: results by risk type |
| `paper-skills-table.png` | Page 8, Table 5: independent paired skill reruns |

These PNGs preserve the source figures and tables without redrawing their contents. Crop coordinates are defined in `CROPS` inside the script, measured in PDF points from the page's top left; page numbers start at one. For a new paper version, update the source URL, version, checksum, coordinates, image dimensions in `site/index.html`, and all figure/table references together. Visually inspect each crop before publishing.

The generated `site/assets/paper-figures.json` records the source URL, version, filename and SHA-256 digest, rendering resolution, page and figure/table numbers, crop coordinates, and image digests. Only the selected crops and their provenance metadata belong in the public website; keep the complete PDF outside `site/`.

## Update the introductory film

The `#film` section below the page title presents the 90-second film. The README poster links to this section. Keep the following public assets together in `site/assets/`:

| Asset | Format |
| --- | --- |
| `lps-bench-film.mp4` | 1920 × 1080, H.264 video with AAC audio |
| `lps-bench-film-poster.jpg` | 1920 × 1080 poster |
| `lps-bench-film.en.vtt` | English WebVTT subtitles |
| `lps-bench-film.zh.vtt` | Simplified Chinese WebVTT subtitles |

The page presents the film in a native HTML video player with its poster, standard playback controls, inline playback, and `preload="none"`. The video and subtitle files are linked directly through their `src` attributes, so playback also works with JavaScript disabled. The film includes English and Chinese text in its frames; optional subtitle tracks start off and can be selected through the player's native controls.

When replacing the film, update its poster and both subtitle files and keep caption timing synchronized. If its duration changes, update the description and README video link text. Preview the film at desktop and phone widths and check keyboard playback, native controls, and subtitle selection before publishing.

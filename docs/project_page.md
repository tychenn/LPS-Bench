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
- After updating the paper-results table in `site/index.html`, run `python scripts/build_project_page_figures.py` to refresh the README chart at `site/assets/results.svg`. The overview diagram is maintained in `site/assets/overview.svg`.
- Use relative asset links so the page works under the `/LPS-Bench/` project path and in local previews.
- Preview the page after changes and check the layout at desktop and mobile widths.
- Update the public paper link and citation only when the corresponding public version and bibliographic details are available. Check displayed results against that paper; repository data may have been revised after the paper's experiments.

The deployment artifact contains **only `site/`**. Keep this directory limited to material approved for public release. Private figures, draft PDFs, raw experiment logs, credentials, and files from `figure/`, `runs/`, or `tmp/` must not be copied into it. Repository documentation outside `site/` is not included in the website artifact.

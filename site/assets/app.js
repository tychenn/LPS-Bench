"use strict";

// Render source text as textContent so case instructions remain inert data.
async function initCaseExplorer() {
  const buttons = [...document.querySelectorAll("[data-risk]")];
  buttons.forEach((button) => {
    button.disabled = true;
  });
  try {
    const response = await fetch("assets/benchmark.json");
    if (!response.ok) throw new Error("Dataset examples are unavailable");
    const dataset = await response.json();
    if (
      !Array.isArray(dataset.risks) ||
      dataset.risks.length !== buttons.length
    ) {
      throw new Error("Incomplete example data");
    }
    function showCase(code, announce = true) {
      const example = dataset.risks.find((risk) => risk.code === code);
      if (!example) return;
      const values = {
        "case-title": example.name,
        "case-domain": example.domain.toUpperCase(),
        "case-description": example.description,
        "case-id": example.case_id,
        "case-tools": `${example.tools.length} available tools`,
        "case-group":
          example.group === "benign"
            ? "Benign user intent"
            : "Adversarial user intent",
        "case-instruction": example.instruction,
        "case-criterion": example.criterion,
      };
      Object.entries(values).forEach(([id, value]) => {
        document.getElementById(id).textContent = value;
      });
      document.getElementById("case-source").href =
        `https://github.com/tychenn/LPS-Bench/blob/main/${example.source}`;
      document.getElementById("case-instruction").scrollTop = 0;
      document.getElementById("case-criterion").scrollTop = 0;
      buttons.forEach((button) =>
        button.setAttribute(
          "aria-pressed",
          String(button.dataset.risk === code),
        ),
      );
      if (announce)
        document.getElementById("case-status").textContent =
          `${example.name}: ${example.case_id}, ${example.domain}. Example updated.`;
    }
    buttons.forEach((button) => {
      button.disabled = false;
      button.addEventListener("click", () => showCase(button.dataset.risk));
    });
    showCase("FA", false);
  } catch (error) {
    // Keep the initial readable example and its direct source link available.
    buttons.forEach((button) => {
      button.disabled = true;
      button.title =
        "Examples could not load. Use the dataset link to browse all cases.";
    });
    const note = document.querySelector(".case-note");
    note.textContent =
      "Showing the initial example. Other examples could not load; browse the dataset on Hugging Face.";
  }
}

function initResults() {
  const chart = document.getElementById("results-chart");
  const controls = [...document.querySelectorAll("[data-result-group]")];
  const results = [...document.querySelectorAll("#results-table tbody tr")].map(
    (row) => ({
      name: row.cells[0].textContent,
      benign: Number(row.cells[1].textContent),
      adversarial: Number(row.cells[2].textContent),
    }),
  );
  function render(group, announce = true) {
    chart.replaceChildren();
    chart.classList.toggle("adversarial-chart", group === "adversarial");
    [...results]
      .sort((a, b) => b[group] - a[group])
      .forEach((model) => {
        const row = document.createElement("div");
        row.className = "chart-row";
        const label = document.createElement("span");
        label.className = "chart-label";
        label.textContent = model.name;
        const track = document.createElement("div");
        track.className = "chart-track";
        track.setAttribute("aria-hidden", "true");
        const bar = document.createElement("div");
        bar.className = "chart-bar";
        bar.style.width = `${model[group]}%`;
        track.append(bar);
        const value = document.createElement("span");
        value.className = "chart-value";
        value.textContent = model[group].toFixed(2);
        value.setAttribute("aria-label", `${model[group].toFixed(2)} percent`);
        row.append(label, track, value);
        chart.append(row);
      });
    const axis = document.createElement("div");
    axis.className = "chart-axis";
    axis.setAttribute("aria-hidden", "true");
    const ticks = document.createElement("div");
    ticks.className = "chart-axis-values";
    ["0", "25", "50", "75", "100%"].forEach((tick) => {
      const label = document.createElement("span");
      label.textContent = tick;
      ticks.append(label);
    });
    axis.append(ticks);
    chart.append(axis);
    chart.setAttribute(
      "aria-label",
      `${group === "benign" ? "Benign" : "Adversarial"} average Safe Rate in percent, sorted highest first`,
    );
    controls.forEach((button) =>
      button.setAttribute(
        "aria-pressed",
        String(button.dataset.resultGroup === group),
      ),
    );
    if (announce)
      document.getElementById("results-status").textContent =
        `Showing ${group} average Safe Rate for 13 models, sorted highest first.`;
  }
  render("benign", false);
  chart.hidden = false;
  document.querySelector(".chart-controls").hidden = false;
  document.querySelector(".results-table-details").open = false;
  controls.forEach((button) =>
    button.addEventListener("click", () => render(button.dataset.resultGroup)),
  );
}

function initCopy() {
  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.hidden = false;
    button.addEventListener("click", async () => {
      const target = document.getElementById(button.dataset.copy);
      const original = button.innerHTML;
      try {
        if (!navigator.clipboard || !window.isSecureContext)
          throw new Error("Clipboard unavailable");
        await navigator.clipboard.writeText(target.textContent.trim());
        button.textContent = "Copied!";
        document.getElementById("copy-status").textContent =
          button.dataset.copy === "bibtex"
            ? "BibTeX citation copied."
            : "Setup commands copied.";
      } catch (error) {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(target);
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = "Text selected";
        document.getElementById("copy-status").textContent =
          "Automatic copying is unavailable. Copy the selected text with your keyboard or browser menu.";
      }
      setTimeout(() => {
        button.innerHTML = original;
      }, 2500);
    });
  });
}

function initFigure() {
  const dialog = document.querySelector(".figure-dialog");
  const trigger = document.querySelector("[data-lightbox]");
  if (typeof dialog.showModal !== "function") return;
  trigger.addEventListener("click", (event) => {
    if (
      event.ctrlKey ||
      event.metaKey ||
      event.shiftKey ||
      event.altKey ||
      event.button !== 0
    )
      return;
    event.preventDefault();
    dialog.showModal();
  });
  dialog
    .querySelector(".dialog-close")
    .addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    const bounds = dialog.getBoundingClientRect();
    if (
      event.clientX < bounds.left ||
      event.clientX > bounds.right ||
      event.clientY < bounds.top ||
      event.clientY > bounds.bottom
    )
      dialog.close();
  });
  dialog.addEventListener("close", () =>
    trigger.focus({ preventScroll: true }),
  );
}

function initNavigation() {
  if (!("IntersectionObserver" in window)) return;
  const links = [...document.querySelectorAll(".nav-links a")];
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        links.forEach((link) => {
          if (link.hash === `#${entry.target.id}`)
            link.setAttribute("aria-current", "location");
          else link.removeAttribute("aria-current");
        });
      });
    },
    { rootMargin: "-64px 0px -60% 0px", threshold: 0 },
  );
  links.forEach((link) => {
    const section = document.querySelector(link.hash);
    if (section) observer.observe(section);
  });
}

initCaseExplorer();
initResults();
initCopy();
initFigure();
initNavigation();

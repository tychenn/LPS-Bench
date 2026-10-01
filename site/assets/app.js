"use strict";

function initFilm() {
  const video = document.getElementById("benchmark-film");
  const launch = document.querySelector("[data-film-play]");
  const subtitles = document.getElementById("film-subtitles");
  const status = document.getElementById("film-status");
  if (!video || !launch || !subtitles || !status) return;

  launch.hidden = false;
  subtitles.closest("label").hidden = false;

  function setSubtitleLanguage(language) {
    Array.from(video.textTracks).forEach((track) => {
      track.mode = track.language === language ? "showing" : "disabled";
    });
  }

  subtitles.addEventListener("change", () =>
    setSubtitleLanguage(subtitles.value),
  );
  video.textTracks.addEventListener("change", () => {
    const visible = Array.from(video.textTracks).find(
      (track) => track.mode === "showing",
    );
    subtitles.value = visible ? visible.language : "off";
  });

  video.addEventListener("playing", () => {
    status.textContent = "";
  });
  video.addEventListener("error", () => {
    status.textContent =
      "The video could not load. Use Download MP4 to open or save the film.";
  });

  launch.addEventListener("click", () => {
    // Fetch the film and optional subtitle files only after a user activates it.
    video.src = video.dataset.src;
    video.querySelectorAll("track[data-src]").forEach((track) => {
      track.src = track.dataset.src;
    });
    setSubtitleLanguage("off");
    subtitles.value = "off";
    subtitles.disabled = false;
    video.hidden = false;
    launch.hidden = true;
    status.textContent = "Loading the film…";
    video.load();
    video.focus({ preventScroll: true });
    const playback = video.play();
    if (playback) {
      playback.catch(() => {
        status.textContent = video.error
          ? "The video could not load. Use Download MP4 to open or save the film."
          : "Press Play in the video controls to start the film.";
      });
    }
  });
}

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
  if (!dialog || typeof dialog.showModal !== "function") return;
  const preview = dialog.querySelector("img");
  const originalLink = dialog.querySelector(":scope > a");
  const title = document.getElementById("figure-dialog-title");
  const scrollRegion = dialog.querySelector(".dialog-image-scroll");
  let activeTrigger;
  document.querySelectorAll("[data-lightbox]").forEach((trigger) => {
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
      const source = trigger.querySelector("img");
      activeTrigger = trigger;
      title.textContent = trigger.dataset.figureTitle;
      preview.src = trigger.href;
      preview.alt = source.alt;
      preview.width = Number(source.getAttribute("width"));
      preview.height = Number(source.getAttribute("height"));
      preview.style.setProperty(
        "--figure-min-width",
        `${Math.min(Number(source.getAttribute("width")), 1100)}px`,
      );
      originalLink.href = trigger.href;
      scrollRegion.setAttribute(
        "aria-label",
        `${trigger.dataset.figureTitle}, scrollable image`,
      );
      dialog.showModal();
      scrollRegion.scrollTo(0, 0);
    });
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
    activeTrigger?.focus({ preventScroll: true }),
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

initFilm();
initCaseExplorer();
initCopy();
initFigure();
initNavigation();

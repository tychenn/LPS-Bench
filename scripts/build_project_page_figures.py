#!/usr/bin/env python3
"""Crop the project's paper figures directly from a local PDF with Poppler."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = ROOT / "tmp" / "papers" / "2602.03255v2.pdf"
SOURCE_URL = "https://arxiv.org/pdf/2602.03255v2"
SOURCE_VERSION = "arXiv:2602.03255v2"
SOURCE_SHA256 = "bb814f8f117186001f287026af0087e2bd4116a27e948471e66dcc74a3526c62"
OUTPUT = ROOT / "site" / "assets"
DPI = 360
# Coordinates are PDF points (1/72 inch), measured from the page's top left.
# Each tuple contains x, y, width, height. Page numbers are one-based.
CROPS = [
    {
        "filename": "paper-overview.png",
        "page": 3,
        "label": "Figure 3",
        "crop_points": (107, 72, 398, 277),
    },
    {
        "filename": "paper-results.png",
        "page": 2,
        "label": "Figure 1",
        "crop_points": (107, 72, 170, 168),
    },
    {
        "filename": "paper-results-table.png",
        "page": 7,
        "label": "Table 3",
        "crop_points": (106, 70, 399, 158),
    },
    {
        "filename": "paper-skills-table.png",
        "page": 8,
        "label": "Table 5",
        "crop_points": (132, 312, 348, 96),
    },
]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pdf",
        type=Path,
        default=DEFAULT_PDF,
        help="Source PDF (default: tmp/papers/2602.03255v2.pdf)",
    )
    args = parser.parse_args()
    pdf = args.pdf.expanduser().resolve()
    if not pdf.is_file():
        parser.error(f"Source PDF does not exist: {pdf}")
    if sha256(pdf) != SOURCE_SHA256:
        parser.error("These crops target arXiv:2602.03255v2. Use that PDF; update the source constants and CROPS together for a new revision.")
    renderer = shutil.which("pdftoppm")
    if not renderer:
        parser.error("pdftoppm is required; install Poppler (for example, apt install poppler-utils).")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    figures = []
    for crop in CROPS:
        x, y, width, height = [round(value * DPI / 72) for value in crop["crop_points"]]
        output = OUTPUT / crop["filename"]
        command = [
            renderer,
            "-f", str(crop["page"]),
            "-l", str(crop["page"]),
            "-r", str(DPI),
            "-x", str(x),
            "-y", str(y),
            "-W", str(width),
            "-H", str(height),
            "-singlefile",
            "-png",
            str(pdf),
            str(output.with_suffix("")),
        ]
        subprocess.run(command, check=True)
        with output.open("rb") as image:
            header = image.read(24)
        if header[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Renderer did not produce a PNG: {output}")
        actual_size = struct.unpack(">II", header[16:24])
        if actual_size != (width, height):
            raise ValueError(
                f"Unexpected crop size for {output.name}: {actual_size}; expected {(width, height)}"
            )
        figures.append({
            **crop,
            "crop_pixels": {"x": x, "y": y, "width": width, "height": height},
            "sha256": sha256(output),
        })
        print(f"Cropped {crop['label']} (page {crop['page']}) to {output.relative_to(ROOT)} ({width} x {height})")

    manifest = {
        "source_filename": pdf.name,
        "source_url": SOURCE_URL,
        "source_version": SOURCE_VERSION,
        "source_sha256": sha256(pdf),
        "renderer": "pdftoppm",
        "dpi": DPI,
        "coordinate_origin": "top-left of PDF page",
        "crop_points_units": "1/72 inch; x, y, width, height",
        "figures": figures,
    }
    target = OUTPUT / "paper-figures.json"
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded source and crop metadata in {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

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
DEFAULT_PDF = ROOT / "847_LPS_Bench_Benchmarking_Saf.pdf"
OUTPUT = ROOT / "site" / "assets"
DPI = 360
# Coordinates are PDF points (1/72 inch), measured from the page's top left.
# Each tuple contains x, y, width, height. Page numbers are one-based.
CROPS = [
    {
        "filename": "paper-overview.png",
        "page": 3,
        "label": "Figure 3",
        "crop_points": (107, 64, 398, 271),
    },
    {
        "filename": "paper-results.png",
        "page": 2,
        "label": "Figure 1",
        "crop_points": (107, 64, 166, 171),
    },
    {
        "filename": "paper-results-table.png",
        "page": 7,
        "label": "Table 3",
        "crop_points": (106, 142, 399, 176),
    },
    {
        "filename": "paper-skills-table.png",
        "page": 8,
        "label": "Table 4",
        "crop_points": (121, 111, 368, 99),
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
        help="Source PDF (default: repository-root 847_LPS_Bench_Benchmarking_Saf.pdf)",
    )
    args = parser.parse_args()
    pdf = args.pdf.expanduser().resolve()
    if not pdf.is_file():
        parser.error(f"Source PDF does not exist: {pdf}")
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

#!/usr/bin/env python3
"""Create the README's static chart from the project page's paper-results table."""

from html import escape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ResultsTable(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.cell = None
        self.row = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        if tag == "table" and dict(attrs).get("id") == "results-table":
            self.active = True
        if self.active and tag == "tr":
            self.row = []
        if self.active and tag in ("td", "th"):
            self.cell = ""

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag):
        if self.active and tag in ("td", "th") and self.cell is not None:
            self.row.append(self.cell.strip())
            self.cell = None
        if self.active and tag == "tr" and len(self.row) == 3:
            try:
                self.rows.append((self.row[0], float(self.row[1]), float(self.row[2])))
            except ValueError:
                pass  # Header row.
        if tag == "table":
            self.active = False


def main():
    parser = ResultsTable()
    parser.feed((ROOT / "site/index.html").read_text())
    if len(parser.rows) != 13:
        raise ValueError("Expected the 13 paper-reported model rows")
    parts = ['''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="660" viewBox="0 0 1200 660" role="img" aria-labelledby="title description">
<title id="title">LPS-Bench paper-reported Safe Rate across 13 models</title>
<desc id="description">Benign and adversarial risk-category averages from Table 3 of the paper. These values refer to the original case revision; the revised dataset requires fresh evaluation. Higher is better.</desc>
<rect x="1" y="1" width="1198" height="658" rx="16" fill="white" stroke="#e0e7e5"/>
<g font-family="Arial, Helvetica, sans-serif">
<text x="34" y="43" font-size="23" font-weight="700" fill="#253c33">Safety across the full trajectory</text>
<text x="34" y="70" font-size="14" fill="#65776c">Average Safe Rate (%) by user-intent group · Higher is better</text>
<rect x="825" y="32" width="15" height="10" rx="2" fill="#6184ad"/><text x="848" y="43" font-size="14" fill="#546b5c">Benign</text>
<rect x="935" y="32" width="15" height="10" rx="2" fill="#bc8964"/><text x="958" y="43" font-size="14" fill="#546b5c">Adversarial</text>''']
    left, width, first_y, stride = 286, 780, 110, 36
    for tick in (0, 25, 50, 75, 100):
        x = left + width * tick / 100
        parts.append(f'<path d="M{x} 102V577" stroke="#e9eeeb"/>')
        parts.append(f'<text x="{x}" y="598" text-anchor="middle" font-size="12" fill="#7b8b80">{tick}</text>')
    for index, (name, benign, adversarial) in enumerate(sorted(parser.rows, key=lambda row: -row[1])):
        y = first_y + index * stride
        parts.append(f'<text x="268" y="{y+16}" text-anchor="end" font-size="15" fill="#415b4b">{escape(name)}</text>')
        for offset, value, color in ((0, benign, "#6184ad"), (13, adversarial, "#bc8964")):
            bar_width = width * value / 100
            parts.append(f'<rect x="{left}" y="{y+offset}" width="{bar_width:.2f}" height="9" rx="2" fill="{color}"/>')
            parts.append(f'<text x="{left+bar_width+7:.2f}" y="{y+offset+9}" font-size="11" fill="#536e5c">{value:.2f}</text>')
    parts.append('''<text x="34" y="628" font-size="13" fill="#62786b">Paper results on the original case revision. Current repository cases require fresh evaluation.</text>
<text x="34" y="648" font-size="11" fill="#7a8c80">Source: LPS-Bench, Table 3 · arXiv:2602.03255</text>
</g></svg>''')
    target = ROOT / "site/assets/results.svg"
    target.write_text("\n".join(parts) + "\n")
    print(f"Rendered 13 model comparisons to {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

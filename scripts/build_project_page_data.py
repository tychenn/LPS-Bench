#!/usr/bin/env python3
"""Export public case examples and dataset counts for the static project page."""

import json
import re
from collections import Counter
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "site" / "assets" / "benchmark.json"
DOMAINS = {
    "webbrowser": "Web Browser",
    "code": "Code",
    "fileio": "File I/O",
    "multi_media": "Multimedia",
    "social_media": "Social Media",
    "OS_operation": "OS Operation",
    "office": "Office",
}
RISKS = [
    ("FA", "False Assumption", "benign", "Guessing missing details instead of asking for clarification.", "webbrowser/FA_1.json"),
    ("TS", "Task Sequence", "benign", "Following an order of operations that violates a safety dependency.", "fileio/TS_1.json"),
    ("OC", "Over-Compliance", "benign", "Following the surface request while overlooking the user's underlying safety needs.", "office/OC_1.json"),
    ("IP", "Inefficient Planning", "benign", "Wasting resources when suitable filtering or batch operations are available.", "code/IP_1.json"),
    ("HS", "Harmless Subtask", "adversarial", "Combining apparently benign steps into a harmful workflow.", "multi_media/HS_1.json"),
    ("MT", "Multi-turn Attack", "adversarial", "Using conversation history to steer an agent toward unsafe actions.", "social_media/MT_1.json"),
    ("EB", "Environment Backdoor", "adversarial", "Planting malicious instructions in tool outputs.", "webbrowser/EB_1.json"),
    ("RC", "Race Condition", "adversarial", "Exploiting the gap between checking a state and acting on it.", "fileio/RC_1.json"),
    ("PI", "Prompt Injection", "adversarial", "Using authority claims and override requests in the user instruction.", "code/PI_1.json"),
]


def main():
    base = [p for p in sorted((ROOT / "examples").glob("*/*.json")) if "_skill_" not in p.stem]
    skill = list((ROOT / "examples").glob("*/*_skill_*.json"))
    domains = Counter(p.parent.name for p in base)
    risks = Counter(p.stem.split("_")[0] for p in base)
    examples = []
    for code, name, group, description, relative in RISKS:
        path = ROOT / "examples" / relative
        case = json.loads(path.read_text())
        examples.append({
            "code": code,
            "name": name,
            "group": group,
            "description": description,
            "count": risks[code],
            "case_id": path.stem,
            "domain": DOMAINS[path.parent.name],
            "source": path.relative_to(ROOT).as_posix(),
            "instruction": case["instruction"],
            "criterion": case["evaluator"]["criterion"],
            "tools": case["MCP"]["tools"],
        })
    payload = {
        "base_cases": len(base),
        "skill_cases": len(skill),
        "benign_cases": sum(risks[code] for code, _, group, _, _ in RISKS if group == "benign"),
        "adversarial_cases": sum(risks[code] for code, _, group, _, _ in RISKS if group == "adversarial"),
        "domains": [{"name": label, "count": domains[key]} for key, label in DOMAINS.items()],
        "risks": examples,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    # Keep the initial case readable and accurate when JavaScript is unavailable.
    page = ROOT / "site/index.html"
    source = page.read_text()
    initial = examples[0]
    for tag, element_id, value in [
        ("div", "case-instruction", initial["instruction"]),
        ("p", "case-criterion", initial["criterion"]),
        ("span", "case-tools", f"{len(initial['tools'])} available tools"),
    ]:
        pattern = rf'(<{tag}[^>]*\bid="{element_id}"[^>]*>).*?(</{tag}>)'
        source, count = re.subn(pattern, lambda match: match[1] + escape(value) + match[2], source, flags=re.S)
        if count != 1:
            raise ValueError(f"Expected one initial-case element: {element_id}")
    page.write_text(source)
    print(f"Exported {len(base)} base cases, {len(skill)} skill cases, and {len(examples)} public examples to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

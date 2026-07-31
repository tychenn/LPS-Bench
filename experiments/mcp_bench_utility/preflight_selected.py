#!/usr/bin/env python3
"""Connect to every required MCP server in the frozen subset once."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--tasks-file", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=int, default=90)
    return parser.parse_args()


def task_servers(data: dict[str, Any]) -> list[str]:
    servers: set[str] = {"Time MCP"}
    for item in data.get("tasks", []):
        value = item.get("server_name", "")
        if isinstance(value, str):
            servers.update(part.strip() for part in value.split("+") if part.strip())
    return sorted(servers)


async def run(args: argparse.Namespace) -> int:
    checkout = args.checkout.resolve()
    tasks_path = args.tasks_file.resolve()
    if args.timeout <= 0:
        raise RuntimeError("Timeout must be positive")
    os.chdir(checkout)
    sys.path.insert(0, str(checkout))
    from benchmark.runner import BenchmarkRunner, ConnectionManager

    runner = BenchmarkRunner(enable_distraction_servers=False)
    commands = await runner.load_commands_config()
    data = json.loads(tasks_path.read_text(encoding="utf-8"))
    report: dict[str, Any] = {"servers": {}, "all_ready": True}
    for server in task_servers(data):
        config = runner.map_server_name_to_config(server, commands)
        if config is None:
            report["servers"][server] = {
                "ready": False,
                "error": "server configuration is missing",
            }
            report["all_ready"] = False
            continue
        try:

            async def connect() -> int:
                async with ConnectionManager([config], True) as manager:
                    return len(manager.all_tools or {})

            tool_count = await asyncio.wait_for(connect(), timeout=args.timeout)
            report["servers"][server] = {
                "ready": tool_count > 0,
                "tool_count": tool_count,
            }
            if tool_count <= 0:
                report["all_ready"] = False
        except Exception as error:
            report["servers"][server] = {
                "ready": False,
                "error": f"{type(error).__name__}: {error}",
            }
            report["all_ready"] = False
        state = "ready" if report["servers"][server]["ready"] else "FAILED"
        print(f"{state}: {server}", flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return 0 if report["all_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run(parse_args())))

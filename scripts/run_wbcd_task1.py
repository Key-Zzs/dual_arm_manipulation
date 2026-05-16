#!/usr/bin/env python3
"""Run WBCD task 1."""

from __future__ import annotations

import argparse

from _bootstrap import bootstrap

ROOT = bootstrap()

from wbcd_task1.core.logger import configure_logging
from wbcd_task1.tasks.wbcd_task1_tube_insert.main import run_wbcd_task1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs" / "wbcd_task1_dry_run.yaml"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    configure_logging()
    result = run_wbcd_task1(args.config, dry_run=args.dry_run)
    print(f"{result.task_name}: {result.status.value} ({len(result.states)} states)")
    for state in result.states:
        print(f"- {state.name}: {state.status.value} attempts={state.attempts} {state.message}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

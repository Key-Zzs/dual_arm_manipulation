#!/usr/bin/env python
from __future__ import annotations
"""Run a configured task."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bimanual_rule_control.tasks.main import run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/task_1.yaml")
    parser.add_argument("--task", default="task_1")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = run(args.config, task_name=args.task, dry_run=args.dry_run)
    print(f"{result.task_name}: success={result.success} message={result.message}")
    for stage in result.stage_results:
        print(f"  - {stage.stage_name}: success={stage.success} message={stage.message}")
    if not result.success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

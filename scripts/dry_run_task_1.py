#!/usr/bin/env python
from __future__ import annotations
"""Run task_1 in dry-run mode."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bimanual_rule_control.tasks.main import run


if __name__ == "__main__":
    result = run("configs/dry_run.yaml", task_name="task_1", dry_run=True)
    print(f"{result.task_name}: success={result.success} message={result.message}")
    for stage in result.stage_results:
        print(f"  - {stage.stage_name}: success={stage.success} message={stage.message}")
    if not result.success:
        raise SystemExit(1)

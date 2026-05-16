"""Public entry point for WBCD task 1."""

from __future__ import annotations

from wbcd_task1.core.config import load_task_config
from wbcd_task1.core.result import TaskResult
from wbcd_task1.tasks.wbcd_task1_tube_insert.context import TaskContext
from wbcd_task1.tasks.wbcd_task1_tube_insert.task import WBCDTask1TubeInsert


def run_wbcd_task1(config_path: str, dry_run: bool = False) -> TaskResult:
    config = load_task_config(config_path, dry_run=True if dry_run else None)
    context = TaskContext.from_config(config)
    task = WBCDTask1TubeInsert(context)
    return task.run()

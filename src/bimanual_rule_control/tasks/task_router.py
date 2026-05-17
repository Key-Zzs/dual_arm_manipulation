from __future__ import annotations
"""Task router."""

from bimanual_rule_control.core.context import TaskContext
from bimanual_rule_control.core.result import TaskResult
from bimanual_rule_control.tasks.task_1 import run_task_1
from bimanual_rule_control.tasks.task_2 import run_task_2
from bimanual_rule_control.tasks.task_3 import run_task_3


def run_task(task_name: str, ctx: TaskContext) -> TaskResult:
    if task_name == "task_1":
        return run_task_1(ctx)
    if task_name == "task_2":
        return run_task_2(ctx)
    if task_name == "task_3":
        return run_task_3(ctx)
    raise ValueError(f"Unknown task: {task_name}")

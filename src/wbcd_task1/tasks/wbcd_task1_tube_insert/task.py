"""WBCD task 1 orchestration."""

from __future__ import annotations

from wbcd_task1.core.config import get_path
from wbcd_task1.core.result import TaskResult, TaskStatus
from wbcd_task1.planning.retry_policy import RetryPolicy
from wbcd_task1.planning.state_machine import StateMachine, StateSpec
from wbcd_task1.tasks.wbcd_task1_tube_insert.context import TaskContext
from wbcd_task1.tasks.wbcd_task1_tube_insert.states import STATE_HANDLERS


DEFAULT_STATE_ORDER = [
    "initialize",
    "locate_tube",
    "align_to_tube",
    "grasp_tube",
    "verify_grasp",
    "locate_rack",
    "locate_empty_hole",
    "align_to_hole",
    "insert_tube",
    "verify_insertion",
]


class WBCDTask1TubeInsert:
    def __init__(self, context: TaskContext):
        self.context = context

    def run(self) -> TaskResult:
        specs = [StateSpec(name, STATE_HANDLERS[name]) for name in DEFAULT_STATE_ORDER]
        retry_policy = RetryPolicy(default_max_retries=int(get_path(self.context.config, "task.max_retries_per_state", 1)))
        state_machine = StateMachine(specs, retry_policy=retry_policy)
        result = TaskResult(
            task_name=str(get_path(self.context.config, "task.name", "wbcd_task1_tube_insert")),
            status=TaskStatus.FAILED,
            dry_run=self.context.dry_run,
        )
        return state_machine.run(self.context, result)

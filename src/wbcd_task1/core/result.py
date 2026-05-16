"""Result types shared by task and planning code."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StateResult:
    name: str
    status: TaskStatus
    message: str = ""
    attempts: int = 1
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status in {TaskStatus.SUCCESS, TaskStatus.SKIPPED}


@dataclass
class TaskResult:
    task_name: str
    status: TaskStatus
    dry_run: bool
    states: list[StateResult] = field(default_factory=list)
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == TaskStatus.SUCCESS

    def add_state(self, result: StateResult) -> None:
        self.states.append(result)

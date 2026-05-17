from __future__ import annotations
"""Common result types."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StageResult:
    stage_name: str
    success: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    task_name: str
    success: bool
    message: str = ""
    stage_results: list[StageResult] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

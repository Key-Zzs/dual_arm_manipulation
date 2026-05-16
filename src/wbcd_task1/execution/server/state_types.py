"""Execution state and response types."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExecutionStatus(str, Enum):
    OK = "ok"
    ERROR = "error"


@dataclass
class ArmState:
    arm: str
    connected: bool = False
    enabled: bool = False
    joints: list[float] = field(default_factory=lambda: [0.0] * 7)
    tcp_pose: list[float] = field(default_factory=lambda: [0.0] * 6)
    gripper_width_m: float | None = None


@dataclass
class ExecutionResponse:
    status: ExecutionStatus
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == ExecutionStatus.OK

    @classmethod
    def ok_response(cls, **data: Any) -> "ExecutionResponse":
        return cls(status=ExecutionStatus.OK, data=data)

    @classmethod
    def error_response(cls, message: str, **data: Any) -> "ExecutionResponse":
        return cls(status=ExecutionStatus.ERROR, message=message, data=data)

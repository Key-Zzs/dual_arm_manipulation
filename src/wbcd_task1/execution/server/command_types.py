"""Execution command definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExecutionCommandType(str, Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    ENABLE = "enable"
    STOP = "stop"
    RESET = "reset"
    GO_HOME = "go_home"
    GET_STATE = "get_state"
    GET_TCP_POSE = "get_tcp_pose"
    GET_JOINTS = "get_joints"
    MOVE_J = "move_j"
    MOVE_P = "move_p"
    SERVO_DELTA_POSE = "servo_delta_pose"
    OPEN_GRIPPER = "open_gripper"
    CLOSE_GRIPPER = "close_gripper"


@dataclass
class ExecutionCommand:
    command_type: ExecutionCommandType
    arm: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    timeout_s: float | None = None

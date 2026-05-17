from __future__ import annotations
"""Dry-run robot client."""

from typing import Any, Sequence

from .base import BaseRobotClient
from .command_types import CommandResult, build_single_arm_delta_action


class MockRobotClient(BaseRobotClient):
    def __init__(self) -> None:
        self.connected = False
        self.closed = False
        self.calls: list[tuple[str, Any]] = []
        self.last_action: dict[str, Any] | None = None

    def connect(self) -> None:
        self.connected = True
        self.closed = False
        self.calls.append(("connect", {}))

    def close(self) -> None:
        self.closed = True
        self.connected = False
        self.calls.append(("close", {}))

    def send_action_cartesian(self, action: dict[str, Any]) -> CommandResult:
        self.last_action = dict(action)
        self.calls.append(("send_action_cartesian", dict(action)))
        return CommandResult(True, "mock cartesian action accepted", {"action": dict(action)})

    def send_arm_delta_pose(self, arm: str, pose_delta: Sequence[float]) -> CommandResult:
        action = build_single_arm_delta_action(arm, pose_delta)
        self.calls.append(("send_arm_delta_pose", {"arm": arm, "pose_delta": list(pose_delta)}))
        return self.send_action_cartesian(action)

    def handle_gripper(self, arm: str, value: float, is_binary: bool = False) -> CommandResult:
        payload = {"arm": arm, "value": float(value), "is_binary": bool(is_binary)}
        self.calls.append(("handle_gripper", payload))
        return CommandResult(True, "mock gripper command accepted", payload)

    def stop(self) -> CommandResult:
        self.calls.append(("stop", {}))
        return CommandResult(True, "mock stop accepted")

    def emergency_stop(self) -> CommandResult:
        self.calls.append(("emergency_stop", {}))
        return CommandResult(True, "mock emergency stop accepted")

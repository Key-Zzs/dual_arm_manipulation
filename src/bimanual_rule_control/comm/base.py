from __future__ import annotations
"""Abstract robot client interface used by planning and tasks."""

from abc import ABC, abstractmethod
from typing import Any, Sequence

from .command_types import CommandResult


class BaseRobotClient(ABC):
    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_action_cartesian(self, action: dict[str, Any]) -> CommandResult:
        raise NotImplementedError

    @abstractmethod
    def send_arm_delta_pose(self, arm: str, pose_delta: Sequence[float]) -> CommandResult:
        raise NotImplementedError

    @abstractmethod
    def handle_gripper(self, arm: str, value: float, is_binary: bool = False) -> CommandResult:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> CommandResult:
        raise NotImplementedError

    @abstractmethod
    def emergency_stop(self) -> CommandResult:
        raise NotImplementedError

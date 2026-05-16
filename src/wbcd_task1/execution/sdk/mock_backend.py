"""In-memory backend for dry-run and tests."""

from __future__ import annotations

import copy

import numpy as np

from wbcd_task1.execution.server.state_types import ArmState


class MockExecutionBackend:
    def __init__(self, arms: list[str] | None = None):
        self.arms = arms or ["right"]
        self.states = {
            arm: ArmState(
                arm=arm,
                connected=False,
                enabled=False,
                joints=[0.0, -0.2, 0.0, 1.87, 0.7 if arm == "right" else -0.7, 0.0, 1.1],
                tcp_pose=[0.3, 0.0, 0.25, 0.0, 0.0, 0.0],
                gripper_width_m=0.1,
            )
            for arm in self.arms
        }
        self.command_log: list[tuple[str, str | None, object]] = []

    def connect(self) -> None:
        for state in self.states.values():
            state.connected = True
        self.command_log.append(("connect", None, None))

    def disconnect(self) -> None:
        for state in self.states.values():
            state.connected = False
            state.enabled = False
        self.command_log.append(("disconnect", None, None))

    def enable(self, arm: str | None = None) -> None:
        for state in self._selected(arm).values():
            state.enabled = True
        self.command_log.append(("enable", arm, None))

    def stop(self, arm: str | None = None) -> None:
        self.command_log.append(("stop", arm, None))

    def reset(self, arm: str | None = None) -> None:
        self.go_home(arm)
        self.command_log.append(("reset", arm, None))

    def go_home(self, arm: str | None = None) -> None:
        for state in self._selected(arm).values():
            state.tcp_pose = [0.3, 0.0, 0.25, 0.0, 0.0, 0.0]
        self.command_log.append(("go_home", arm, None))

    def get_state(self, arm: str | None = None) -> dict[str, ArmState]:
        return copy.deepcopy(self._selected(arm))

    def get_tcp_pose(self, arm: str) -> list[float]:
        return list(self.states[arm].tcp_pose)

    def get_joints(self, arm: str) -> list[float]:
        return list(self.states[arm].joints)

    def move_j(self, arm: str, joints: list[float], delta: bool = False) -> None:
        current = np.asarray(self.states[arm].joints, dtype=float)
        target = current + np.asarray(joints, dtype=float) if delta else np.asarray(joints, dtype=float)
        self.states[arm].joints = target.astype(float).tolist()
        self.command_log.append(("move_j", arm, self.states[arm].joints))

    def move_p(self, arm: str, pose: list[float], delta: bool = False) -> None:
        current = np.asarray(self.states[arm].tcp_pose, dtype=float)
        target = current + np.asarray(pose, dtype=float) if delta else np.asarray(pose, dtype=float)
        self.states[arm].tcp_pose = target.astype(float).tolist()
        self.command_log.append(("move_p", arm, self.states[arm].tcp_pose))

    def servo_delta_pose(self, arm: str, delta_pose: list[float]) -> None:
        self.move_p(arm, delta_pose, delta=True)
        self.command_log.append(("servo_delta_pose", arm, delta_pose))

    def open_gripper(self, arm: str, width_m: float = 0.1, force: float = 1.0) -> None:
        self.states[arm].gripper_width_m = float(width_m)
        self.command_log.append(("open_gripper", arm, {"width_m": width_m, "force": force}))

    def close_gripper(self, arm: str, width_m: float = 0.0, force: float = 1.0) -> None:
        self.states[arm].gripper_width_m = float(width_m)
        self.command_log.append(("close_gripper", arm, {"width_m": width_m, "force": force}))

    def _selected(self, arm: str | None) -> dict[str, ArmState]:
        if arm is None:
            return self.states
        if arm not in self.states:
            raise ValueError(f"Unknown arm: {arm}")
        return {arm: self.states[arm]}

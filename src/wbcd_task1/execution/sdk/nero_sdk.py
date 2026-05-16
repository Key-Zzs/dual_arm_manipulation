"""Thin adapter around the retained pyAgxArm SDK."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from wbcd_task1.execution.server.state_types import ArmState


@dataclass
class _ArmHandle:
    arm: str
    channel: str
    robot: Any = None
    gripper: Any = None
    connected: bool = False
    enabled: bool = False


class NeroSDKBackend:
    """Hardware backend for Nero arms.

    The heavy SDK stays in the repository as ``pyAgxArm``. This adapter is the
    only execution-layer entry point that imports it.
    """

    HOME_JOINTS = {
        "left": [0.0, -0.2, 0.0, 1.87, -0.7, 0.0, 1.1],
        "right": [0.0, -0.2, 0.0, 1.87, 0.7, 0.0, 1.1],
    }

    def __init__(self, arms: list[str] | None = None, enable_gripper: bool = True):
        self.arms = arms or ["right"]
        self.enable_gripper = enable_gripper
        self.handles = {
            arm: _ArmHandle(arm=arm, channel=f"can_{arm}")
            for arm in self.arms
        }

    def connect(self) -> None:
        from pyAgxArm import AgxArmFactory, create_agx_arm_config

        for handle in self.handles.values():
            if handle.connected:
                continue
            cfg = create_agx_arm_config(robot="nero", comm="can", channel=handle.channel)
            handle.robot = AgxArmFactory.create_arm(cfg)
            if self.enable_gripper:
                handle.gripper = handle.robot.init_effector(handle.robot.OPTIONS.EFFECTOR.AGX_GRIPPER)
            handle.robot.connect()
            time.sleep(0.3)
            if hasattr(handle.robot, "set_normal_mode"):
                handle.robot.set_normal_mode()
            handle.connected = True

    def disconnect(self) -> None:
        for handle in self.handles.values():
            try:
                if handle.robot is not None and hasattr(handle.robot, "disconnect"):
                    handle.robot.disconnect()
            finally:
                handle.connected = False
                handle.enabled = False

    def enable(self, arm: str | None = None) -> None:
        for handle in self._selected(arm).values():
            self._require_robot(handle)
            start_t = time.monotonic()
            while not handle.robot.enable(255):
                if time.monotonic() - start_t > 5.0:
                    raise TimeoutError(f"{handle.arm} arm enable timeout")
                time.sleep(0.01)
            handle.enabled = True

    def stop(self, arm: str | None = None) -> None:
        for handle in self._selected(arm).values():
            if handle.robot is not None and hasattr(handle.robot, "electronic_emergency_stop"):
                handle.robot.electronic_emergency_stop()

    def reset(self, arm: str | None = None) -> None:
        for handle in self._selected(arm).values():
            self._require_robot(handle)
            if hasattr(handle.robot, "reset"):
                handle.robot.reset()

    def go_home(self, arm: str | None = None) -> None:
        for handle in self._selected(arm).values():
            self.move_j(handle.arm, self.HOME_JOINTS[handle.arm], delta=False)

    def get_state(self, arm: str | None = None) -> dict[str, ArmState]:
        states: dict[str, ArmState] = {}
        for name, handle in self._selected(arm).items():
            states[name] = ArmState(
                arm=name,
                connected=handle.connected,
                enabled=handle.enabled,
                joints=self.get_joints(name) if handle.robot is not None else [0.0] * 7,
                tcp_pose=self.get_tcp_pose(name) if handle.robot is not None else [0.0] * 6,
                gripper_width_m=self._read_gripper_width(handle),
            )
        return states

    def get_tcp_pose(self, arm: str) -> list[float]:
        handle = self._handle(arm)
        self._require_robot(handle)
        result = handle.robot.get_tcp_pose()
        return list(result.msg) if result is not None else [0.0] * 6

    def get_joints(self, arm: str) -> list[float]:
        handle = self._handle(arm)
        self._require_robot(handle)
        result = handle.robot.get_joint_angles()
        return list(result.msg) if result is not None else [0.0] * 7

    def move_j(self, arm: str, joints: list[float], delta: bool = False) -> None:
        handle = self._handle(arm)
        self._require_robot(handle)
        values = np.asarray(joints, dtype=float).reshape(7)
        if delta:
            values = np.asarray(self.get_joints(arm), dtype=float) + values
        handle.robot.move_j(values.astype(float).tolist())

    def move_p(self, arm: str, pose: list[float], delta: bool = False) -> None:
        handle = self._handle(arm)
        self._require_robot(handle)
        values = np.asarray(pose, dtype=float).reshape(6)
        if delta:
            values = np.asarray(self.get_tcp_pose(arm), dtype=float) + values
        handle.robot.move_p(values.astype(float).tolist())

    def servo_delta_pose(self, arm: str, delta_pose: list[float]) -> None:
        self.move_p(arm, delta_pose, delta=True)

    def open_gripper(self, arm: str, width_m: float = 0.1, force: float = 1.0) -> None:
        self._move_gripper(arm, width_m, force)

    def close_gripper(self, arm: str, width_m: float = 0.0, force: float = 1.0) -> None:
        self._move_gripper(arm, width_m, force)

    def _move_gripper(self, arm: str, width_m: float, force: float) -> None:
        handle = self._handle(arm)
        if handle.gripper is None:
            raise RuntimeError(f"{arm} gripper is not available")
        width = max(0.0, min(float(width_m), 0.1))
        handle.gripper.move_gripper(width=width, force=float(force))

    def _selected(self, arm: str | None) -> dict[str, _ArmHandle]:
        if arm is None:
            return self.handles
        return {arm: self._handle(arm)}

    def _handle(self, arm: str) -> _ArmHandle:
        if arm not in self.handles:
            raise ValueError(f"Unknown arm: {arm}")
        return self.handles[arm]

    @staticmethod
    def _require_robot(handle: _ArmHandle) -> None:
        if handle.robot is None:
            raise RuntimeError(f"{handle.arm} robot is not connected")

    @staticmethod
    def _read_gripper_width(handle: _ArmHandle) -> float | None:
        if handle.gripper is None:
            return None
        status = handle.gripper.get_gripper_status()
        return float(status.msg.width) if status is not None else None

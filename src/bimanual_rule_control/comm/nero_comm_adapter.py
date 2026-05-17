from __future__ import annotations
"""Lightweight adapter over the preserved dual_agilex_nero communication code."""

from typing import Any, Sequence

from .base import BaseRobotClient
from .command_types import CommandResult, build_single_arm_delta_action, normalize_arm
from .dual_agilex_nero.config_nero import NeroDualArmConfig
from .dual_agilex_nero.nero_dual_arm import NeroDualArm


class NeroCommAdapter(BaseRobotClient):
    """Expose a small planning-facing API while reusing the verified Nero code.

    The preserved `NeroDualArm` still owns `connect`, `send_action`,
    `send_action_cartesian`, and `handle_gripper`. This adapter only translates
    higher-level task commands into that existing interface and separates
    ordinary socket close from explicit emergency stop.
    """

    def __init__(self, config: dict[str, Any] | None = None, dry_run: bool | None = None) -> None:
        self.raw_config = config or {}
        self.comm_config = self.raw_config.get("comm", self.raw_config)
        self.gripper_config = self.raw_config.get("gripper", self.raw_config)
        task_config = self.raw_config.get("task", {})
        self.dry_run = bool(task_config.get("dry_run", False) if dry_run is None else dry_run)
        self.debug = bool(self.comm_config.get("debug", False) or self.dry_run)
        self.last_action: dict[str, Any] | None = None
        self.last_gripper_command: dict[str, Any] | None = None

        self.nero_config = NeroDualArmConfig(
            robot_ip=str(self.comm_config.get("robot_ip", "127.0.0.1")),
            robot_port=int(self.comm_config.get("robot_port", 4242)),
            use_gripper=bool(self.gripper_config.get("use_gripper", True)),
            gripper_max_open=float(self.gripper_config.get("gripper_max_open", 0.1)),
            gripper_force=float(self.gripper_config.get("gripper_force", 2.0)),
            gripper_reverse=bool(self.gripper_config.get("gripper_reverse", False)),
            close_threshold=float(self.gripper_config.get("close_threshold", 0.5)),
            debug=self.debug,
        )
        self._robot = NeroDualArm(self.nero_config)
        self._robot.action_send_freq = float(self.comm_config.get("action_send_freq", 100.0))
        self._robot.action_send_dt = 1.0 / self._robot.action_send_freq

    @property
    def robot(self) -> NeroDualArm:
        return self._robot

    def connect(self) -> None:
        if self.dry_run:
            self._robot.is_connected = True
            return
        self._robot.connect(calibrate=False)
        rpc_client = getattr(self._robot, "_robot", None)
        if rpc_client is None or getattr(rpc_client, "server", None) is None:
            raise RuntimeError(
                "Nero zerorpc client is not connected. Check zerorpc installation "
                "and the external agilex_teleop server address."
            )

    def close(self) -> None:
        """Close the zerorpc socket without calling robot_stop.

        The original `NeroDualArmClient.close()` calls `robot_stop()` for both
        arms. The external server implementation may treat that as electronic
        emergency stop, so this adapter keeps ordinary close separate.
        """
        rpc_client = getattr(self._robot, "_robot", None)
        server = getattr(rpc_client, "server", None)
        if server is not None:
            try:
                server.close()
            finally:
                rpc_client.server = None
        self._robot.is_connected = False

    def send_action_cartesian(self, action: dict[str, Any]) -> CommandResult:
        self.last_action = dict(action)
        if self.dry_run:
            return CommandResult(True, "dry-run cartesian action accepted", {"action": dict(action)})
        try:
            self._robot.send_action_cartesian(action)
            return CommandResult(True, "cartesian action sent", {"action": dict(action)})
        except Exception as exc:
            return CommandResult(False, "cartesian action failed", {"action": dict(action)}, error=str(exc))

    def send_arm_delta_pose(self, arm: str, pose_delta: Sequence[float]) -> CommandResult:
        action = build_single_arm_delta_action(arm, pose_delta)
        return self.send_action_cartesian(action)

    def handle_gripper(self, arm: str, value: float, is_binary: bool = False) -> CommandResult:
        arm_name = normalize_arm(arm)
        self.last_gripper_command = {"arm": arm_name, "value": float(value), "is_binary": bool(is_binary)}
        if self.dry_run:
            return CommandResult(True, "dry-run gripper command accepted", dict(self.last_gripper_command))
        try:
            # Reuse the original normalization, reverse, width, and force logic.
            self._robot.handle_gripper(arm_name, float(value), is_binary=is_binary)
            return CommandResult(True, "gripper command sent", dict(self.last_gripper_command))
        except Exception as exc:
            return CommandResult(False, "gripper command failed", dict(self.last_gripper_command), error=str(exc))

    def stop(self) -> CommandResult:
        if self.dry_run:
            return CommandResult(True, "dry-run soft stop accepted")
        return CommandResult(False, "soft stop is not supported by the preserved Nero client")

    def emergency_stop(self) -> CommandResult:
        if self.dry_run:
            return CommandResult(True, "dry-run emergency stop accepted")
        rpc_client = getattr(self._robot, "_robot", None)
        if rpc_client is None:
            return CommandResult(False, "Nero client is not initialized")
        errors: list[str] = []
        for arm in ("left_robot", "right_robot"):
            try:
                rpc_client.stop(arm)
            except Exception as exc:
                errors.append(f"{arm}: {exc}")
        if errors:
            return CommandResult(False, "emergency stop failed", error="; ".join(errors))
        return CommandResult(True, "emergency stop sent")

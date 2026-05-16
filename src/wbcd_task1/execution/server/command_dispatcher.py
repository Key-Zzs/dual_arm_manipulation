"""Command dispatcher for execution backends."""

from __future__ import annotations

from dataclasses import asdict

from wbcd_task1.execution.sdk.backend import ExecutionBackend
from wbcd_task1.execution.server.command_types import ExecutionCommand, ExecutionCommandType
from wbcd_task1.execution.server.safety_guard import SafetyGuard
from wbcd_task1.execution.server.state_types import ArmState, ExecutionResponse


class CommandDispatcher:
    def __init__(self, backend: ExecutionBackend, safety_guard: SafetyGuard):
        self.backend = backend
        self.safety_guard = safety_guard

    def dispatch(self, command: ExecutionCommand) -> ExecutionResponse:
        try:
            data = self._dispatch_or_raise(command)
            return ExecutionResponse.ok_response(**data)
        except Exception as exc:
            return ExecutionResponse.error_response(str(exc), command=command.command_type.value)

    def _dispatch_or_raise(self, command: ExecutionCommand) -> dict:
        cmd = command.command_type
        arm = command.arm
        payload = command.payload

        if cmd == ExecutionCommandType.CONNECT:
            self.backend.connect()
            return {}
        if cmd == ExecutionCommandType.DISCONNECT:
            self.backend.disconnect()
            return {}
        if cmd == ExecutionCommandType.ENABLE:
            self.backend.enable(arm)
            return {}
        if cmd == ExecutionCommandType.STOP:
            self.backend.stop(arm)
            return {}
        if cmd == ExecutionCommandType.RESET:
            self.backend.reset(arm)
            return {}
        if cmd == ExecutionCommandType.GO_HOME:
            self.backend.go_home(arm)
            return {}
        if cmd == ExecutionCommandType.GET_STATE:
            return {"state": self._state_to_dict(self.backend.get_state(arm))}
        if cmd == ExecutionCommandType.GET_TCP_POSE:
            self._require_arm(arm)
            return {"tcp_pose": self.backend.get_tcp_pose(arm)}
        if cmd == ExecutionCommandType.GET_JOINTS:
            self._require_arm(arm)
            return {"joints": self.backend.get_joints(arm)}
        if cmd == ExecutionCommandType.MOVE_J:
            self._require_arm(arm)
            self.backend.move_j(arm, payload["joints"], bool(payload.get("delta", False)))
            return {}
        if cmd == ExecutionCommandType.MOVE_P:
            self._require_arm(arm)
            pose = list(payload["pose"])
            if not payload.get("delta", False):
                self.safety_guard.check_target_pose(pose)
            self.backend.move_p(arm, pose, bool(payload.get("delta", False)))
            return {}
        if cmd == ExecutionCommandType.SERVO_DELTA_POSE:
            self._require_arm(arm)
            delta_pose = self.safety_guard.clamp_delta_pose(payload["delta_pose"])
            self.safety_guard.wait_for_servo_period()
            self.backend.servo_delta_pose(arm, delta_pose)
            return {"delta_pose": delta_pose}
        if cmd == ExecutionCommandType.OPEN_GRIPPER:
            self._require_arm(arm)
            self.backend.open_gripper(
                arm,
                float(payload.get("width_m", 0.1)),
                float(payload.get("force", 1.0)),
            )
            return {}
        if cmd == ExecutionCommandType.CLOSE_GRIPPER:
            self._require_arm(arm)
            self.backend.close_gripper(
                arm,
                float(payload.get("width_m", 0.0)),
                float(payload.get("force", 1.0)),
            )
            return {}
        raise ValueError(f"Unsupported command: {cmd}")

    @staticmethod
    def _require_arm(arm: str | None) -> None:
        if arm is None:
            raise ValueError("Command requires an arm")

    @staticmethod
    def _state_to_dict(states: dict[str, ArmState]) -> dict:
        return {name: asdict(state) for name, state in states.items()}

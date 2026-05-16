"""In-process execution service for Agilex Nero hardware."""

from __future__ import annotations

from wbcd_task1.execution.sdk.mock_backend import MockExecutionBackend
from wbcd_task1.execution.sdk.nero_interface_backend import NeroInterfaceServerBackend
from wbcd_task1.execution.server.command_dispatcher import CommandDispatcher
from wbcd_task1.execution.server.command_types import ExecutionCommand, ExecutionCommandType
from wbcd_task1.execution.server.safety_guard import SafetyGuard


def build_dispatcher(config: dict, *, dry_run: bool = False) -> CommandDispatcher:
    execution_cfg = config.get("execution", {})
    robot_cfg = execution_cfg.get("robot", {})
    arms = list(robot_cfg.get("arms", ["right"]))
    safety = SafetyGuard.from_config(execution_cfg.get("safety", {}))
    if dry_run:
        backend = MockExecutionBackend(arms=arms)
    else:
        backend = NeroInterfaceServerBackend(
            arms=arms,
            enable_gripper=bool(robot_cfg.get("enable_gripper", True)),
            tcp_offset_enabled=bool(robot_cfg.get("tcp_offset_enabled", False)),
            limit_z=float(execution_cfg.get("safety", {}).get("min_tcp_z_m", 0.07)),
        )
    return CommandDispatcher(backend=backend, safety_guard=safety)


class AgilexExecutionServer:
    """Local facade exposing the command vocabulary used by task code."""

    def __init__(self, config: dict | None = None, *, dry_run: bool = False):
        self.config = config or {}
        self.dispatcher = build_dispatcher(self.config, dry_run=dry_run)

    def dispatch(self, command_type: str, payload: dict | None = None, arm: str | None = None) -> dict:
        command = ExecutionCommand(
            command_type=ExecutionCommandType(command_type),
            arm=arm,
            payload=payload or {},
        )
        response = self.dispatcher.dispatch(command)
        return {
            "ok": response.ok,
            "status": response.status.value,
            "message": response.message,
            "data": response.data,
        }

    def connect(self) -> dict:
        return self.dispatch(ExecutionCommandType.CONNECT.value)

    def go_home(self, arm: str | None = None) -> dict:
        return self.dispatch(ExecutionCommandType.GO_HOME.value, arm=arm)

    def get_state(self, arm: str | None = None) -> dict:
        return self.dispatch(ExecutionCommandType.GET_STATE.value, arm=arm)

    def stop(self, arm: str | None = None) -> dict:
        return self.dispatch(ExecutionCommandType.STOP.value, arm=arm)


def create_execution_service(config: dict, *, dry_run: bool = False) -> AgilexExecutionServer:
    """Build an in-process execution service.

    Perception, planning, and execution run on the same machine for this task,
    so the active architecture does not need a network transport.
    """

    return AgilexExecutionServer(config=config, dry_run=dry_run)

"""Zerorpc execution server for Agilex Nero hardware."""

from __future__ import annotations

from wbcd_task1.execution.sdk.mock_backend import MockExecutionBackend
from wbcd_task1.execution.sdk.nero_sdk import NeroSDKBackend
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
        backend = NeroSDKBackend(
            arms=arms,
            enable_gripper=bool(robot_cfg.get("enable_gripper", True)),
        )
    return CommandDispatcher(backend=backend, safety_guard=safety)


class AgilexExecutionServer:
    """RPC facade exposing the command vocabulary used by task code."""

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


def start_server(config: dict, host: str, port: int, *, dry_run: bool = False) -> None:
    try:
        import zerorpc
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("zerorpc is required to start the execution server") from exc

    server = zerorpc.Server(AgilexExecutionServer(config=config, dry_run=dry_run))
    server.bind(f"tcp://{host}:{port}")
    server.run()

"""Task context assembly."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from wbcd_task1.core.config import get_path
from wbcd_task1.execution.server.agilex_server import build_dispatcher
from wbcd_task1.execution.server.command_types import ExecutionCommand, ExecutionCommandType
from wbcd_task1.perception.cameras.camera_manager import CameraManager
from wbcd_task1.perception.result_types import Detection2D


class ExecutionClient:
    """In-process execution API used by planning/task code."""

    def __init__(self, dispatcher, default_arm: str):
        self.dispatcher = dispatcher
        self.default_arm = default_arm

    def command(self, command_type: ExecutionCommandType, arm: str | None = None, **payload):
        return self.dispatcher.dispatch(
            ExecutionCommand(command_type=command_type, arm=arm or self.default_arm, payload=payload)
        )

    def connect(self):
        return self.dispatcher.dispatch(ExecutionCommand(ExecutionCommandType.CONNECT))

    def enable(self, arm: str | None = None):
        return self.command(ExecutionCommandType.ENABLE, arm=arm)

    def go_home(self, arm: str | None = None):
        return self.command(ExecutionCommandType.GO_HOME, arm=arm)

    def servo_delta_pose(self, delta_pose: list[float], arm: str | None = None):
        return self.command(ExecutionCommandType.SERVO_DELTA_POSE, arm=arm, delta_pose=delta_pose)

    def open_gripper(self, arm: str | None = None, width_m: float = 0.1, force: float = 1.0):
        return self.command(ExecutionCommandType.OPEN_GRIPPER, arm=arm, width_m=width_m, force=force)

    def close_gripper(self, arm: str | None = None, width_m: float = 0.0, force: float = 1.0):
        return self.command(ExecutionCommandType.CLOSE_GRIPPER, arm=arm, width_m=width_m, force=force)

    def get_state(self, arm: str | None = None):
        return self.command(ExecutionCommandType.GET_STATE, arm=arm)


@dataclass
class TaskContext:
    config: dict[str, Any]
    dry_run: bool
    default_arm: str
    execution: ExecutionClient
    cameras: CameraManager | None = None
    observations: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "TaskContext":
        dry_run = bool(get_path(config, "task.dry_run", False))
        default_arm = str(get_path(config, "task.default_arm", "right"))
        dispatcher = build_dispatcher(config, dry_run=dry_run)
        camera_cfg = get_path(config, "perception.cameras", {})
        cameras = CameraManager(camera_cfg) if camera_cfg else None
        return cls(
            config=config,
            dry_run=dry_run,
            default_arm=default_arm,
            execution=ExecutionClient(dispatcher, default_arm=default_arm),
            cameras=cameras,
        )

    def mock_detection(self, label: str) -> Detection2D:
        return Detection2D(label=label, confidence=1.0, center_px=(320.0, 240.0))

from __future__ import annotations
"""Task runtime context."""

from dataclasses import dataclass, field
from typing import Any

from bimanual_rule_control.comm.base import BaseRobotClient


@dataclass
class TaskContext:
    config: dict[str, Any]
    dry_run: bool
    robot_client: BaseRobotClient
    camera_manager: Any | None = None

    tube_detector: Any | None = None
    rack_detector: Any | None = None
    hole_detector: Any | None = None
    tag_detector: Any | None = None

    tube_detection: Any | None = None
    rack_detection: Any | None = None
    hole_detection: Any | None = None
    target_pose: Any | None = None

    current_arm: str = "right"
    retry_counts: dict[str, int] = field(default_factory=dict)

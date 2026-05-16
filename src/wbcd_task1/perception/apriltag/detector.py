"""AprilTag pose detector placeholder."""

from __future__ import annotations

from wbcd_task1.perception.base import CameraFrame
from wbcd_task1.perception.result_types import PoseEstimate


class AprilTagDetector:
    def __init__(self, family: str = "tag36h11", tag_size_m: float = 0.025, enabled: bool = True):
        self.name = "AprilTagDetector"
        self.family = family
        self.tag_size_m = float(tag_size_m)
        self.enabled = bool(enabled)

    def estimate(self, frame: CameraFrame) -> list[PoseEstimate]:
        if not self.enabled:
            return []
        return []

from __future__ import annotations
"""AprilTag detector skeleton with delayed dependency import."""

from typing import Any

from bimanual_rule_control.perception.base import BaseDetector
from bimanual_rule_control.perception.result_types import DetectionResult


class AprilTagDetector(BaseDetector):
    def __init__(self) -> None:
        try:
            from pupil_apriltags import Detector
        except ImportError:
            try:
                from apriltag import Detector
            except ImportError as exc:
                raise RuntimeError("pupil_apriltags or apriltag is required for AprilTagDetector") from exc
        self.detector = Detector()

    def detect(self, frame: Any = None) -> DetectionResult:
        # TODO: adapt detector outputs into AprilTagDetection.
        return DetectionResult(success=False, message="AprilTag detector output adapter not implemented")

from __future__ import annotations
"""OpenCV tube detector skeleton."""

from typing import Any

from bimanual_rule_control.perception.base import BaseDetector
from bimanual_rule_control.perception.result_types import DetectionResult


class OpenCVTubeDetector(BaseDetector):
    def detect(self, frame: Any = None) -> DetectionResult:
        raise NotImplementedError("OpenCV tube detection is not implemented yet")

from __future__ import annotations
"""OpenCV rack detector skeleton."""

from typing import Any

from bimanual_rule_control.perception.base import BaseDetector
from bimanual_rule_control.perception.result_types import DetectionResult


class OpenCVRackDetector(BaseDetector):
    def detect(self, frame: Any = None) -> DetectionResult:
        raise NotImplementedError("OpenCV rack detection is not implemented yet")

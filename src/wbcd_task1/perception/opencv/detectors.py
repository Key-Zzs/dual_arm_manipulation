"""OpenCV detector placeholders."""

from __future__ import annotations

from wbcd_task1.perception.base import CameraFrame
from wbcd_task1.perception.result_types import Detection2D


class _BaseOpenCVDetector:
    label = "object"

    def __init__(self, params: dict | None = None):
        self.params = params or {}
        self.name = self.__class__.__name__

    def detect(self, frame: CameraFrame) -> list[Detection2D]:
        if self.params.get("mock", False):
            center = tuple(self.params.get("center_px", (320, 240)))
            return [Detection2D(label=self.label, confidence=1.0, center_px=center)]
        return []


class OpenCVTubeCapDetector(_BaseOpenCVDetector):
    label = "tube_cap"


class OpenCVRackDetector(_BaseOpenCVDetector):
    label = "rack"


class OpenCVHoleDetector(_BaseOpenCVDetector):
    label = "hole"

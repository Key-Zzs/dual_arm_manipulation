"""YOLO adapter placeholders."""

from __future__ import annotations

from wbcd_task1.perception.base import CameraFrame
from wbcd_task1.perception.result_types import Detection2D


class YOLODetector:
    def __init__(self, model_path: str | None = None, params: dict | None = None):
        self.name = "YOLODetector"
        self.model_path = model_path
        self.params = params or {}
        self.model = None

    def detect(self, frame: CameraFrame) -> list[Detection2D]:
        if self.model is None:
            return []
        raise NotImplementedError("Wire YOLO inference here")


class YOLOSegmentor(YOLODetector):
    def __init__(self, model_path: str | None = None, params: dict | None = None):
        super().__init__(model_path=model_path, params=params)
        self.name = "YOLOSegmentor"

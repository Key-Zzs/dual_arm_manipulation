from __future__ import annotations
"""YOLO detector skeleton with delayed ultralytics import."""

from typing import Any

from bimanual_rule_control.perception.base import BaseDetector
from bimanual_rule_control.perception.result_types import DetectionResult


class YOLODetector(BaseDetector):
    def __init__(self, model_path: str) -> None:
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError("ultralytics is required for YOLODetector") from exc
        self.model = YOLO(model_path)

    def detect(self, frame: Any = None) -> DetectionResult:
        # TODO: adapt ultralytics outputs into DetectionResult.
        return DetectionResult(success=False, message="YOLO detector output adapter not implemented")

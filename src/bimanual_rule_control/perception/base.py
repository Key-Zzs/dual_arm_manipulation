from __future__ import annotations
"""Detector base classes."""

from abc import ABC, abstractmethod
from typing import Any

from .result_types import DetectionResult, HoleDetection, RackDetection, TubeDetection


class BaseDetector(ABC):
    @abstractmethod
    def detect(self, frame: Any = None) -> DetectionResult:
        raise NotImplementedError


class MockDetector(BaseDetector):
    def __init__(self, kind: str = "generic", success: bool = True) -> None:
        self.kind = kind
        self.success = success

    def detect(self, frame: Any = None) -> DetectionResult:
        if self.kind == "tube":
            payload = TubeDetection(label="mock_tube", confidence=1.0, pose=[0, 0, 0, 0, 0, 0])
        elif self.kind == "rack":
            payload = RackDetection(label="mock_rack", confidence=1.0, pose=[0, 0, 0, 0, 0, 0])
        elif self.kind == "hole":
            payload = HoleDetection(label="mock_hole", confidence=1.0, pose=[0, 0, 0, 0, 0, 0])
        else:
            payload = {"kind": self.kind}
        return DetectionResult(success=self.success, message=f"mock {self.kind} detection", data=payload)

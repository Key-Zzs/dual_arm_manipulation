"""Perception interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from wbcd_task1.perception.result_types import Detection2D


@dataclass
class CameraFrame:
    camera_name: str
    color: np.ndarray | None = None
    depth: np.ndarray | None = None
    timestamp_s: float = 0.0
    intrinsics: dict | None = None


class Camera(Protocol):
    name: str

    def connect(self) -> None: ...

    def disconnect(self) -> None: ...

    def read(self) -> CameraFrame: ...


class Detector(Protocol):
    name: str

    def detect(self, frame: CameraFrame) -> list[Detection2D]: ...

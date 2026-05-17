from __future__ import annotations
"""Mock camera for dry-run and tests."""

import time

from .base_camera import BaseCamera
from .frame_types import CameraFrame


class MockCamera(BaseCamera):
    def __init__(self, name: str = "mock") -> None:
        self.name = name
        self.is_open = False

    def open(self) -> None:
        self.is_open = True

    def read(self) -> CameraFrame:
        return CameraFrame(color=None, depth=None, timestamp=time.time(), camera_name=self.name)

    def close(self) -> None:
        self.is_open = False

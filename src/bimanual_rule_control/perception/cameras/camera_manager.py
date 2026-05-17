from __future__ import annotations
"""Camera manager."""

from .base_camera import BaseCamera


class CameraManager:
    def __init__(self, cameras: dict[str, BaseCamera] | None = None) -> None:
        self.cameras = cameras or {}

    def open(self) -> None:
        for camera in self.cameras.values():
            camera.open()

    def read_all(self):
        return {name: camera.read() for name, camera in self.cameras.items()}

    def close(self) -> None:
        for camera in self.cameras.values():
            camera.close()

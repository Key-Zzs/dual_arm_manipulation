"""Camera manager for task-level configs."""

from __future__ import annotations

from wbcd_task1.perception.base import CameraFrame
from wbcd_task1.perception.cameras.realsense_camera import MockCamera, RealSenseCamera


class CameraManager:
    def __init__(self, cameras: dict):
        self.cameras = {
            name: self._build_camera(name, cfg or {})
            for name, cfg in cameras.items()
        }

    def connect_all(self) -> None:
        for camera in self.cameras.values():
            camera.connect()

    def disconnect_all(self) -> None:
        for camera in self.cameras.values():
            camera.disconnect()

    def read(self, name: str) -> CameraFrame:
        if name not in self.cameras:
            raise KeyError(f"Unknown camera: {name}")
        return self.cameras[name].read()

    def read_all(self) -> dict[str, CameraFrame]:
        return {name: camera.read() for name, camera in self.cameras.items()}

    @staticmethod
    def _build_camera(name: str, config: dict):
        camera_type = str(config.get("type", "mock")).lower()
        if camera_type == "realsense":
            return RealSenseCamera(name, config)
        return MockCamera(name, config)

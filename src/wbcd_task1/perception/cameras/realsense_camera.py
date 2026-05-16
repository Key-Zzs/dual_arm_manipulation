"""RealSense camera wrapper with a mock fallback for dry-run."""

from __future__ import annotations

import time

import numpy as np

from wbcd_task1.perception.base import CameraFrame


class MockCamera:
    def __init__(self, name: str, config: dict | None = None):
        self.name = name
        self.config = config or {}
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def read(self) -> CameraFrame:
        width = int(self.config.get("width", 640))
        height = int(self.config.get("height", 480))
        color = np.zeros((height, width, 3), dtype=np.uint8)
        depth = np.zeros((height, width), dtype=np.float32)
        return CameraFrame(
            camera_name=self.name,
            color=color,
            depth=depth,
            timestamp_s=time.time(),
            intrinsics={"fx": 1.0, "fy": 1.0, "cx": width / 2.0, "cy": height / 2.0},
        )


class RealSenseCamera:
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self.pipeline = None
        self.connected = False

    def connect(self) -> None:
        try:
            import pyrealsense2 as rs
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("pyrealsense2 is required for RealSenseCamera") from exc

        self._rs = rs
        self.pipeline = rs.pipeline()
        rs_config = rs.config()
        serial = self.config.get("serial")
        if serial:
            rs_config.enable_device(str(serial))
        width = int(self.config.get("width", 640))
        height = int(self.config.get("height", 480))
        fps = int(self.config.get("fps", 30))
        rs_config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        if self.config.get("enable_depth", True):
            rs_config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
        self.pipeline.start(rs_config)
        self.connected = True

    def disconnect(self) -> None:
        if self.pipeline is not None:
            self.pipeline.stop()
        self.connected = False

    def read(self) -> CameraFrame:
        if self.pipeline is None:
            raise RuntimeError(f"Camera is not connected: {self.name}")
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        color = np.asanyarray(color_frame.get_data()) if color_frame else None
        depth = np.asanyarray(depth_frame.get_data()) if depth_frame else None
        return CameraFrame(camera_name=self.name, color=color, depth=depth, timestamp_s=time.time())

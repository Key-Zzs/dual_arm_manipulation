from __future__ import annotations
"""RealSense camera wrapper with delayed dependency import."""

import time
from typing import Any

from .base_camera import BaseCamera
from .frame_types import CameraFrame


class RealSenseCamera(BaseCamera):
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.pipeline = None
        self.name = str(config.get("name", "realsense"))

    def open(self) -> None:
        try:
            import pyrealsense2 as rs
        except ImportError as exc:
            raise RuntimeError("pyrealsense2 is required to open a RealSense camera") from exc
        self.pipeline = rs.pipeline()
        # TODO: apply width/height/fps/depth settings.
        self.pipeline.start()

    def read(self) -> CameraFrame:
        if self.pipeline is None:
            raise RuntimeError("RealSense camera is not open")
        frames = self.pipeline.wait_for_frames()
        color = frames.get_color_frame()
        depth = frames.get_depth_frame()
        return CameraFrame(color=color, depth=depth, timestamp=time.time(), camera_name=self.name)

    def close(self) -> None:
        if self.pipeline is not None:
            self.pipeline.stop()
            self.pipeline = None

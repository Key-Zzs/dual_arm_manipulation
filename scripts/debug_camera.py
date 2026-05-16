#!/usr/bin/env python3
"""Read one frame from configured cameras."""

from __future__ import annotations

import argparse

from _bootstrap import bootstrap

ROOT = bootstrap()

from wbcd_task1.core.config import get_path, load_task_config
from wbcd_task1.perception.cameras.camera_manager import CameraManager


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs" / "debug_camera.yaml"))
    args = parser.parse_args()
    config = load_task_config(args.config)
    manager = CameraManager(get_path(config, "perception.cameras", {}))
    manager.connect_all()
    try:
        frames = manager.read_all()
        for name, frame in frames.items():
            shape = None if frame.color is None else tuple(frame.color.shape)
            print(f"{name}: color_shape={shape} timestamp={frame.timestamp_s:.3f}")
    finally:
        manager.disconnect_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

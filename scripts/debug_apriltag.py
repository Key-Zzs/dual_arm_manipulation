#!/usr/bin/env python3
"""Run AprilTag placeholder detector."""

from __future__ import annotations

import argparse

from _bootstrap import bootstrap

ROOT = bootstrap()

from wbcd_task1.core.config import get_path, load_task_config
from wbcd_task1.perception.apriltag import AprilTagDetector
from wbcd_task1.perception.cameras.camera_manager import CameraManager


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs" / "debug_perception.yaml"))
    args = parser.parse_args()
    config = load_task_config(args.config)
    cameras = CameraManager(get_path(config, "perception.cameras", {}))
    cameras.connect_all()
    try:
        frame = next(iter(cameras.read_all().values()))
        apriltag_cfg = get_path(config, "perception.detectors.apriltag", {})
        detector = AprilTagDetector(
            family=str(apriltag_cfg.get("family", "tag36h11")),
            tag_size_m=float(apriltag_cfg.get("tag_size_m", 0.025)),
            enabled=bool(apriltag_cfg.get("enabled", False)),
        )
        estimates = detector.estimate(frame)
        print(f"AprilTag estimates: {len(estimates)}")
    finally:
        cameras.disconnect_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

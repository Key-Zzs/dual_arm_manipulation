#!/usr/bin/env python3
"""Run perception placeholder detectors on one mock frame."""

from __future__ import annotations

import argparse

from _bootstrap import bootstrap

ROOT = bootstrap()

from wbcd_task1.core.config import get_path, load_task_config
from wbcd_task1.perception.cameras.camera_manager import CameraManager
from wbcd_task1.perception.opencv import OpenCVHoleDetector, OpenCVRackDetector, OpenCVTubeCapDetector


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs" / "debug_perception.yaml"))
    args = parser.parse_args()
    config = load_task_config(args.config)
    cameras = CameraManager(get_path(config, "perception.cameras", {}))
    cameras.connect_all()
    try:
        frame = next(iter(cameras.read_all().values()))
        detector_cfg = get_path(config, "perception.detectors", {})
        detectors = [
            OpenCVTubeCapDetector({**detector_cfg.get("tube_cap", {}).get("params", {}), "mock": True}),
            OpenCVRackDetector({**detector_cfg.get("rack", {}).get("params", {}), "mock": True}),
            OpenCVHoleDetector({**detector_cfg.get("hole", {}).get("params", {}), "mock": True}),
        ]
        for detector in detectors:
            detections = detector.detect(frame)
            print(f"{detector.name}: {len(detections)} detections")
    finally:
        cameras.disconnect_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

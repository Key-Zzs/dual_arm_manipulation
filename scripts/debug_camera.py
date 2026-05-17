#!/usr/bin/env python
from __future__ import annotations
"""Camera debug placeholder."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bimanual_rule_control.perception.cameras.camera_manager import CameraManager
from bimanual_rule_control.perception.cameras.mock_camera import MockCamera


if __name__ == "__main__":
    manager = CameraManager({"wrist": MockCamera("wrist"), "head": MockCamera("head")})
    manager.open()
    print(manager.read_all())
    manager.close()

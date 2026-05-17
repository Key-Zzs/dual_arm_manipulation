from __future__ import annotations
"""OpenCV detector skeletons."""

from .hole_detector import OpenCVHoleDetector
from .rack_detector import OpenCVRackDetector
from .tube_detector import OpenCVTubeDetector

__all__ = ["OpenCVTubeDetector", "OpenCVRackDetector", "OpenCVHoleDetector"]

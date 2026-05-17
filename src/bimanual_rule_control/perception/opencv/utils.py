from __future__ import annotations
"""OpenCV utility placeholders."""


def ensure_opencv_available():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("opencv-python is required for OpenCV perception") from exc
    return cv2

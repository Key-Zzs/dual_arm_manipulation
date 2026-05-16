"""Success/failure predicates."""

from __future__ import annotations

from wbcd_task1.perception.result_types import Detection2D


def has_detection(detections: list[Detection2D], label: str, min_confidence: float = 0.1) -> bool:
    return any(d.label == label and d.confidence >= min_confidence for d in detections)


def pixel_error_below(error_px: float, threshold_px: float) -> bool:
    return abs(float(error_px)) <= float(threshold_px)


def gripper_closed(width_m: float | None, threshold_m: float = 0.02) -> bool:
    return width_m is not None and float(width_m) <= threshold_m

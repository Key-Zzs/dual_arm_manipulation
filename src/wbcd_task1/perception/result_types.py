"""Perception result data classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Detection2D:
    label: str
    confidence: float
    center_px: tuple[float, float]
    bbox_xyxy: tuple[float, float, float, float] | None = None
    mask: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PoseEstimate:
    frame_id: str
    translation: tuple[float, float, float]
    quaternion_xyzw: tuple[float, float, float, float]
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PerceptionResult:
    detections: list[Detection2D] = field(default_factory=list)
    pose_estimates: list[PoseEstimate] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

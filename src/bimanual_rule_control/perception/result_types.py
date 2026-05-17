from __future__ import annotations
"""Perception result dataclasses."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DetectionResult:
    success: bool
    message: str = ""
    data: Any | None = None


@dataclass
class TubeDetection:
    label: str
    confidence: float
    pose: list[float] | None = None
    bbox: tuple[int, int, int, int] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TubeCapDetection:
    label: str
    confidence: float
    pose: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RackDetection:
    label: str
    confidence: float
    pose: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HoleDetection:
    label: str
    confidence: float
    pose: list[float] | None = None
    occupied: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AprilTagDetection:
    tag_id: int
    confidence: float
    pose: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

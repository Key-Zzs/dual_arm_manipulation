from __future__ import annotations
"""Perception interfaces and detector skeletons."""

from .base import BaseDetector, MockDetector
from .result_types import DetectionResult

__all__ = ["BaseDetector", "MockDetector", "DetectionResult"]

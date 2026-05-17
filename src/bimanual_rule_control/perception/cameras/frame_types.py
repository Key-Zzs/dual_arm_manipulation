from __future__ import annotations
"""Camera frame containers."""

from dataclasses import dataclass
from typing import Any


@dataclass
class CameraFrame:
    color: Any | None = None
    depth: Any | None = None
    timestamp: float | None = None
    camera_name: str = ""

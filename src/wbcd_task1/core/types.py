"""Common geometry and task data types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ArmName(str, Enum):
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True)
class Pose6D:
    """Pose as [x, y, z, roll, pitch, yaw]."""

    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float

    def as_list(self) -> list[float]:
        return [self.x, self.y, self.z, self.roll, self.pitch, self.yaw]

    @classmethod
    def from_iterable(cls, values: list[float] | tuple[float, ...]) -> "Pose6D":
        if len(values) != 6:
            raise ValueError(f"Pose6D needs 6 values, got {len(values)}")
        return cls(*(float(v) for v in values))


@dataclass(frozen=True)
class JointVector:
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.values) != 7:
            raise ValueError(f"Nero arm needs 7 joints, got {len(self.values)}")

    def as_list(self) -> list[float]:
        return [float(v) for v in self.values]

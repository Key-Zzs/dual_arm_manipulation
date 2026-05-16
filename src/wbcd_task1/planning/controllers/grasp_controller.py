"""Grasp controller placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GraspController:
    pregrasp_height_m: float
    descend_step_m: float
    lift_after_grasp_m: float

    def descend_delta(self) -> list[float]:
        return [0.0, 0.0, -self.descend_step_m, 0.0, 0.0, 0.0]

    def lift_delta(self) -> list[float]:
        return [0.0, 0.0, self.lift_after_grasp_m, 0.0, 0.0, 0.0]

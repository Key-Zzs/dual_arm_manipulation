"""Visual servo controller placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VisualServoController:
    max_step_m: float = 0.003

    def pixel_error_to_delta_pose(self, error_xy_px: tuple[float, float]) -> list[float]:
        scale = self.max_step_m / 100.0
        dx = max(-self.max_step_m, min(self.max_step_m, -float(error_xy_px[0]) * scale))
        dy = max(-self.max_step_m, min(self.max_step_m, -float(error_xy_px[1]) * scale))
        return [dx, dy, 0.0, 0.0, 0.0, 0.0]

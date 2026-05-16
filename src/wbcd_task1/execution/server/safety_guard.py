"""Safety clamps for execution commands."""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np


@dataclass
class SafetyLimits:
    max_linear_step_m: float = 0.005
    max_angular_step_rad: float = 0.05
    max_servo_rate_hz: float = 30.0
    enable_motion_limits: bool = True
    min_tcp_z_m: float = 0.07


class SafetyGuard:
    def __init__(self, limits: SafetyLimits):
        self.limits = limits
        self._last_servo_time = 0.0

    @classmethod
    def from_config(cls, config: dict) -> "SafetyGuard":
        return cls(
            SafetyLimits(
                max_linear_step_m=float(config.get("max_linear_step_m", 0.005)),
                max_angular_step_rad=float(config.get("max_angular_step_rad", 0.05)),
                max_servo_rate_hz=float(config.get("max_servo_rate_hz", 30.0)),
                enable_motion_limits=bool(config.get("enable_motion_limits", True)),
                min_tcp_z_m=float(config.get("min_tcp_z_m", 0.07)),
            )
        )

    def clamp_delta_pose(self, delta_pose: list[float]) -> list[float]:
        values = np.asarray(delta_pose, dtype=float).reshape(-1)
        if values.size != 6:
            raise ValueError(f"Expected 6 pose delta values, got {values.size}")
        if not self.limits.enable_motion_limits:
            return values.tolist()
        values[:3] = np.clip(
            values[:3],
            -self.limits.max_linear_step_m,
            self.limits.max_linear_step_m,
        )
        values[3:] = np.clip(
            values[3:],
            -self.limits.max_angular_step_rad,
            self.limits.max_angular_step_rad,
        )
        return values.astype(float).tolist()

    def check_target_pose(self, pose: list[float]) -> None:
        if len(pose) != 6:
            raise ValueError(f"Expected 6 pose values, got {len(pose)}")
        if self.limits.enable_motion_limits and float(pose[2]) < self.limits.min_tcp_z_m:
            raise ValueError(
                f"Target z={pose[2]:.4f} below min_tcp_z_m={self.limits.min_tcp_z_m:.4f}"
            )

    def wait_for_servo_period(self) -> None:
        if self.limits.max_servo_rate_hz <= 0:
            return
        now = time.monotonic()
        period = 1.0 / self.limits.max_servo_rate_hz
        remaining = period - (now - self._last_servo_time)
        if remaining > 0:
            time.sleep(remaining)
        self._last_servo_time = time.monotonic()

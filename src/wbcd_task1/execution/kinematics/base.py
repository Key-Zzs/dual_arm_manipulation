"""Kinematics solver interface."""

from __future__ import annotations

from typing import Protocol


class KinematicsSolver(Protocol):
    def init_state(self, current_q: list[float]) -> None: ...

    def fk_pose(self, q: list[float]) -> list[float]: ...

    def solve(self, target_pose: list[float], limit_output_step: bool = True) -> list[float] | None: ...

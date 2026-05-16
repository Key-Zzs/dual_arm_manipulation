"""Insertion controller placeholder."""

from __future__ import annotations

from dataclasses import dataclass

from wbcd_task1.planning.motion.search_pattern import generate_cross_search_pattern


@dataclass
class InsertionController:
    descend_step_m: float
    max_insert_depth_m: float
    search_step_m: float
    search_radius_m: float

    def descend_delta(self) -> list[float]:
        return [0.0, 0.0, -self.descend_step_m, 0.0, 0.0, 0.0]

    def search_offsets(self) -> list[tuple[float, float, float]]:
        return generate_cross_search_pattern(self.search_step_m, self.search_radius_m)

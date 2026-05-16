"""Search pattern generation."""

from __future__ import annotations


def generate_cross_search_pattern(step_m: float, radius_m: float) -> list[tuple[float, float, float]]:
    step = float(step_m)
    radius = float(radius_m)
    if step <= 0:
        raise ValueError("step_m must be positive")
    if radius < 0:
        raise ValueError("radius_m must be non-negative")
    points = [(0.0, 0.0, 0.0)]
    k_max = int(radius // step)
    for k in range(1, k_max + 1):
        distance = k * step
        points.extend(
            [
                (distance, 0.0, 0.0),
                (-distance, 0.0, 0.0),
                (0.0, distance, 0.0),
                (0.0, -distance, 0.0),
            ]
        )
    return points

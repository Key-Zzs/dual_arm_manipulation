from __future__ import annotations
"""Pose planning placeholders."""

from bimanual_rule_control.core.context import TaskContext


def _pose_from_config(ctx: TaskContext, section: str, key: str) -> list[float]:
    values = ctx.config.get("planning", {}).get(section, {}).get(key, [0, 0, 0, 0, 0, 0])
    values = [float(value) for value in values]
    if len(values) != 6:
        raise ValueError(f"Configured pose {section}.{key} must contain 6 values")
    return values


def plan_tube_grasp_pose(ctx: TaskContext) -> list[float]:
    if ctx.dry_run:
        return _pose_from_config(ctx, "grasp", "mock_grasp_delta")
    # TODO: compute grasp delta from tube detection and calibration.
    return _pose_from_config(ctx, "grasp", "mock_grasp_delta")


def plan_preinsert_pose(ctx: TaskContext) -> list[float]:
    if ctx.dry_run:
        return _pose_from_config(ctx, "insertion", "mock_insert_delta")
    # TODO: compute preinsert pose from rack/hole detection.
    return _pose_from_config(ctx, "insertion", "mock_insert_delta")


def plan_insertion_pose(ctx: TaskContext) -> list[float]:
    if ctx.dry_run:
        return _pose_from_config(ctx, "insertion", "mock_insert_delta")
    # TODO: compute insertion descent and alignment correction.
    return _pose_from_config(ctx, "insertion", "mock_insert_delta")

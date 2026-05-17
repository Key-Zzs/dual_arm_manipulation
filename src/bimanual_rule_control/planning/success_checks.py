from __future__ import annotations
"""Stage success checks."""

from bimanual_rule_control.core.context import TaskContext


def check_tube_detected(ctx: TaskContext) -> bool:
    return ctx.dry_run or ctx.tube_detection is not None


def check_grasp_success(ctx: TaskContext) -> bool:
    return ctx.dry_run or ctx.tube_detection is not None


def check_rack_detected(ctx: TaskContext) -> bool:
    return ctx.dry_run or ctx.rack_detection is not None


def check_hole_detected(ctx: TaskContext) -> bool:
    return ctx.dry_run or ctx.hole_detection is not None


def check_insert_success(ctx: TaskContext) -> bool:
    return ctx.dry_run or ctx.hole_detection is not None

from __future__ import annotations
"""Retry policy helpers."""

from bimanual_rule_control.core.context import TaskContext


def get_stage_max_retries(ctx: TaskContext, stage_name: str) -> int:
    stages_cfg = ctx.config.get("stages", {})
    task_cfg = ctx.config.get("task", {})
    stage_cfg = stages_cfg.get(stage_name, {})
    return int(stage_cfg.get("max_retries", task_cfg.get("max_retries_per_stage", 1)))


def should_retry(ctx: TaskContext, stage_name: str) -> bool:
    count = ctx.retry_counts.get(stage_name, 0)
    return count < get_stage_max_retries(ctx, stage_name)


def record_retry(ctx: TaskContext, stage_name: str) -> int:
    ctx.retry_counts[stage_name] = ctx.retry_counts.get(stage_name, 0) + 1
    return ctx.retry_counts[stage_name]

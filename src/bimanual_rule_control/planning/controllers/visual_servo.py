from __future__ import annotations
"""Visual servo controller skeleton."""

from bimanual_rule_control.comm.command_types import CommandResult
from bimanual_rule_control.core.context import TaskContext


def run_visual_servo(ctx: TaskContext, arm: str | None = None) -> CommandResult:
    # TODO: use image-space error to produce bounded 6D correction steps.
    return CommandResult(True, "visual servo placeholder completed")

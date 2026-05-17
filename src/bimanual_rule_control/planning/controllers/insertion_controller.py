from __future__ import annotations
"""Insertion controller skeleton."""

from bimanual_rule_control.comm.command_types import CommandResult
from bimanual_rule_control.core.context import TaskContext


def execute_insertion(ctx: TaskContext, pose_delta: list[float], arm: str | None = None) -> CommandResult:
    target_arm = arm or ctx.current_arm
    result = ctx.robot_client.send_arm_delta_pose(target_arm, pose_delta)
    if not result.success:
        return result
    return CommandResult(True, "insertion command sequence completed")


def run_micro_search(ctx: TaskContext, arm: str | None = None) -> CommandResult:
    # TODO: implement spiral/grid micro-search from visual or force feedback.
    return CommandResult(True, "micro-search placeholder completed")

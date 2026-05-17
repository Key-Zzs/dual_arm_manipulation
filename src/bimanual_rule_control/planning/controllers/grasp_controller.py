from __future__ import annotations
"""Grasp controller skeleton."""

from bimanual_rule_control.comm.command_types import CommandResult
from bimanual_rule_control.core.context import TaskContext


def execute_grasp(ctx: TaskContext, pose_delta: list[float], arm: str | None = None) -> CommandResult:
    target_arm = arm or ctx.current_arm
    move_result = ctx.robot_client.send_arm_delta_pose(target_arm, pose_delta)
    if not move_result.success:
        return move_result
    grip_result = ctx.robot_client.handle_gripper(target_arm, 0.0, is_binary=False)
    if not grip_result.success:
        return grip_result
    return CommandResult(True, "grasp command sequence completed")

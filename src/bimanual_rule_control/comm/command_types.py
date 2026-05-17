from __future__ import annotations
"""Command schema helpers for dual-arm communication."""

from dataclasses import dataclass, field
from typing import Any, Sequence

CARTESIAN_AXES = ("x", "y", "z", "rx", "ry", "rz")
ARM_SIDES = ("left", "right")
ARM_TO_RPC_NAME = {"left": "left_robot", "right": "right_robot"}


@dataclass
class CommandResult:
    success: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


def normalize_arm(arm: str) -> str:
    arm_name = str(arm).lower()
    if arm_name not in ARM_SIDES:
        raise ValueError(f"Unknown arm '{arm}'. Expected one of {ARM_SIDES}.")
    return arm_name


def validate_pose_delta(pose_delta: Sequence[float]) -> list[float]:
    values = [float(value) for value in pose_delta]
    if len(values) != 6:
        raise ValueError(f"Expected 6D pose delta [x, y, z, rx, ry, rz], got {len(values)} values.")
    return values


def empty_dual_arm_action() -> dict[str, float]:
    return {f"{arm}_delta_ee_pose.{axis}": 0.0 for arm in ARM_SIDES for axis in CARTESIAN_AXES}


def build_single_arm_delta_action(arm: str, pose_delta: Sequence[float]) -> dict[str, float]:
    arm_name = normalize_arm(arm)
    values = validate_pose_delta(pose_delta)
    action = empty_dual_arm_action()
    for axis, value in zip(CARTESIAN_AXES, values):
        action[f"{arm_name}_delta_ee_pose.{axis}"] = value
    return action

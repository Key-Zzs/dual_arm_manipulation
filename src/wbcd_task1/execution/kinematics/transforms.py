"""Small transform utilities used by execution and tests."""

from __future__ import annotations

import math

import numpy as np


def rpy_to_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return np.array(
        [
            [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
            [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
            [-sp, cp * sr, cp * cr],
        ],
        dtype=float,
    )


def matrix_to_rpy(rotation: np.ndarray) -> np.ndarray:
    rotation = np.asarray(rotation, dtype=float).reshape(3, 3)
    pitch = math.atan2(-rotation[2, 0], math.hypot(rotation[0, 0], rotation[1, 0]))
    if abs(math.cos(pitch)) < 1e-9:
        roll = 0.0
        yaw = math.atan2(-rotation[0, 1], rotation[1, 1])
    else:
        roll = math.atan2(rotation[2, 1], rotation[2, 2])
        yaw = math.atan2(rotation[1, 0], rotation[0, 0])
    return np.array([roll, pitch, yaw], dtype=float)


def pose6_to_matrix(pose: list[float] | tuple[float, ...] | np.ndarray) -> np.ndarray:
    pose = np.asarray(pose, dtype=float).reshape(-1)
    if pose.size != 6:
        raise ValueError(f"Expected 6 pose values, got {pose.size}")
    transform = np.eye(4, dtype=float)
    transform[:3, :3] = rpy_to_matrix(float(pose[3]), float(pose[4]), float(pose[5]))
    transform[:3, 3] = pose[:3]
    return transform


def matrix_to_pose6(transform: np.ndarray) -> np.ndarray:
    transform = np.asarray(transform, dtype=float).reshape(4, 4)
    rpy = matrix_to_rpy(transform[:3, :3])
    return np.concatenate([transform[:3, 3], rpy])


def invert_transform(transform: np.ndarray) -> np.ndarray:
    transform = np.asarray(transform, dtype=float).reshape(4, 4)
    out = np.eye(4, dtype=float)
    out[:3, :3] = transform[:3, :3].T
    out[:3, 3] = -out[:3, :3] @ transform[:3, 3]
    return out


def compose_transform(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.asarray(a, dtype=float).reshape(4, 4) @ np.asarray(b, dtype=float).reshape(4, 4)


def transform_point(transform: np.ndarray, point: list[float] | tuple[float, ...] | np.ndarray) -> np.ndarray:
    point = np.asarray(point, dtype=float).reshape(3)
    point_h = np.ones(4, dtype=float)
    point_h[:3] = point
    return (np.asarray(transform, dtype=float).reshape(4, 4) @ point_h)[:3]

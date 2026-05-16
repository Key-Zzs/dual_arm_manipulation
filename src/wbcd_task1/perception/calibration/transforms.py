"""Calibration transform helpers."""

from __future__ import annotations

import numpy as np


def transform_from_config(config: dict) -> np.ndarray:
    translation = np.asarray(config.get("translation", [0.0, 0.0, 0.0]), dtype=float).reshape(3)
    qx, qy, qz, qw = np.asarray(config.get("quaternion", [0.0, 0.0, 0.0, 1.0]), dtype=float).reshape(4)
    norm = float(np.linalg.norm([qx, qy, qz, qw]))
    if norm == 0:
        raise ValueError("Quaternion norm must be non-zero")
    qx, qy, qz, qw = qx / norm, qy / norm, qz / norm, qw / norm
    rotation = np.array(
        [
            [1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
            [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
            [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)],
        ],
        dtype=float,
    )
    transform = np.eye(4, dtype=float)
    transform[:3, :3] = rotation
    transform[:3, 3] = translation
    return transform

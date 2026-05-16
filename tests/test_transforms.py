import numpy as np

from wbcd_task1.execution.kinematics.transforms import (
    compose_transform,
    invert_transform,
    matrix_to_pose6,
    pose6_to_matrix,
    transform_point,
)


def test_transform_inverse_is_identity():
    transform = pose6_to_matrix([0.1, -0.2, 0.3, 0.2, -0.1, 0.4])
    identity = compose_transform(transform, invert_transform(transform))
    assert np.allclose(identity, np.eye(4), atol=1e-8)


def test_pose_round_trip_translation_and_point():
    pose = [0.1, 0.2, 0.3, 0.0, 0.0, 0.0]
    transform = pose6_to_matrix(pose)
    round_trip = matrix_to_pose6(transform)
    point = transform_point(transform, [1.0, 2.0, 3.0])
    assert np.allclose(round_trip, pose)
    assert np.allclose(point, [1.1, 2.2, 3.3])

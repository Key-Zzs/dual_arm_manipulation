from __future__ import annotations
from bimanual_rule_control.comm.mock_client import MockRobotClient


def test_mock_client_commands():
    client = MockRobotClient()
    client.connect()
    assert client.connected

    action = {f"{arm}_delta_ee_pose.{axis}": 0.0 for arm in ("left", "right") for axis in ("x", "y", "z", "rx", "ry", "rz")}
    assert client.send_action_cartesian(action).success
    assert client.send_arm_delta_pose("right", [0, 0, 0, 0, 0, 0]).success
    assert client.handle_gripper("right", 1.0).success
    assert client.stop().success
    assert client.emergency_stop().success

    client.close()
    assert client.closed

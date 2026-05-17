from __future__ import annotations
from bimanual_rule_control.comm.nero_comm_adapter import NeroCommAdapter


def _adapter():
    return NeroCommAdapter(
        {
            "task": {"dry_run": True},
            "comm": {"robot_ip": "127.0.0.1", "robot_port": 4242, "debug": True},
            "gripper": {"use_gripper": True, "gripper_max_open": 0.1, "gripper_force": 2.0},
        },
        dry_run=True,
    )


def test_send_arm_delta_pose_generates_12_key_action_right():
    adapter = _adapter()
    result = adapter.send_arm_delta_pose("right", [1, 2, 3, 4, 5, 6])
    assert result.success
    action = result.data["action"]
    assert len(action) == 12
    assert action["right_delta_ee_pose.x"] == 1.0
    assert action["right_delta_ee_pose.rz"] == 6.0
    assert action["left_delta_ee_pose.x"] == 0.0


def test_send_arm_delta_pose_generates_12_key_action_left():
    adapter = _adapter()
    result = adapter.send_arm_delta_pose("left", [1, 2, 3, 4, 5, 6])
    assert result.success
    action = result.data["action"]
    assert action["left_delta_ee_pose.x"] == 1.0
    assert action["right_delta_ee_pose.x"] == 0.0


def test_gripper_command_adapter_entry():
    adapter = _adapter()
    result = adapter.handle_gripper("left", 1.0)
    assert result.success
    assert adapter.last_gripper_command == {"arm": "left", "value": 1.0, "is_binary": False}

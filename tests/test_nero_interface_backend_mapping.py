from wbcd_task1.execution.sdk.nero_interface_backend import NeroInterfaceServerBackend
from wbcd_task1.execution.server.command_dispatcher import CommandDispatcher
from wbcd_task1.execution.server.command_types import ExecutionCommand, ExecutionCommandType
from wbcd_task1.execution.server.safety_guard import SafetyGuard, SafetyLimits


class FakeRobot:
    def __init__(self, calls):
        self.calls = calls

    def reset(self):
        self.calls.append(("robot.reset",))


class FakeNeroDualArmServer:
    def __init__(self, gripper_enabled=True, tcp_offset_enabled=False, limit_z=0.07):
        self.calls = []
        self.right_robot = FakeRobot(self.calls)
        self.calls.append(("__init__", gripper_enabled, tcp_offset_enabled, limit_z))

    def right_robot_get_joint_positions(self):
        self.calls.append(("right_robot_get_joint_positions",))
        return [0.0] * 7

    def right_robot_get_ee_pose(self):
        self.calls.append(("right_robot_get_ee_pose",))
        return [0.0] * 6

    def right_robot_go_home(self):
        self.calls.append(("right_robot_go_home",))

    def right_robot_move_to_joint_positions(self, joints, delta=False):
        self.calls.append(("right_robot_move_to_joint_positions", joints, delta))

    def right_robot_move_to_ee_pose(self, pose, delta=False):
        self.calls.append(("right_robot_move_to_ee_pose", pose, delta))

    def servo_p_OL(self, robot_arm, pose, delta=False):
        self.calls.append(("servo_p_OL", robot_arm, pose, delta))
        return True

    def right_gripper_goto(self, width, force=1.0):
        self.calls.append(("right_gripper_goto", width, force))
        return True

    def right_gripper_get_state(self):
        self.calls.append(("right_gripper_get_state",))
        return {"width": 0.04}

    def robot_stop(self, robot_arm):
        self.calls.append(("robot_stop", robot_arm))
        return True


def test_real_backend_maps_commands_to_migrated_nero_server_methods():
    backend = NeroInterfaceServerBackend(
        arms=["right"],
        enable_gripper=True,
        limit_z=0.0,
        server_cls=FakeNeroDualArmServer,
    )
    dispatcher = CommandDispatcher(
        backend=backend,
        safety_guard=SafetyGuard(SafetyLimits(min_tcp_z_m=0.0, max_servo_rate_hz=0.0)),
    )

    def dispatch(command_type, **kwargs):
        response = dispatcher.dispatch(ExecutionCommand(command_type, **kwargs))
        assert response.ok, response.message
        return response

    dispatch(ExecutionCommandType.CONNECT)
    dispatch(ExecutionCommandType.GET_STATE, arm="right")
    dispatch(ExecutionCommandType.GET_JOINTS, arm="right")
    dispatch(ExecutionCommandType.GET_TCP_POSE, arm="right")
    dispatch(ExecutionCommandType.MOVE_J, arm="right", payload={"joints": [0.1] * 7})
    dispatch(ExecutionCommandType.MOVE_P, arm="right", payload={"pose": [0.1, 0.0, 0.2, 0.0, 0.0, 0.0]})
    dispatch(ExecutionCommandType.SERVO_DELTA_POSE, arm="right", payload={"delta_pose": [0.001, 0, 0, 0, 0, 0]})
    dispatch(ExecutionCommandType.OPEN_GRIPPER, arm="right", payload={"width_m": 0.08, "force": 1.0})
    dispatch(ExecutionCommandType.CLOSE_GRIPPER, arm="right", payload={"width_m": 0.0, "force": 1.0})
    dispatch(ExecutionCommandType.RESET, arm="right")
    dispatch(ExecutionCommandType.GO_HOME, arm="right")
    dispatch(ExecutionCommandType.STOP, arm="right")

    called = [call[0] for call in backend._server.calls]
    assert "right_robot_move_to_joint_positions" in called
    assert "right_robot_move_to_ee_pose" in called
    assert "servo_p_OL" in called
    assert called.count("right_gripper_goto") == 2
    assert "robot.reset" in called
    assert "right_robot_go_home" in called
    assert "robot_stop" in called

"""Backend that calls the migrated NeroDualArmServer methods.

The old execution behavior lives in ``NeroDualArmServer``:
``left/right_robot_move_to_joint_positions``, ``left/right_robot_move_to_ee_pose``,
``servo_p_OL``, gripper calls, and state reads. This adapter maps the new
task-level command vocabulary to those migrated server methods.
"""

from __future__ import annotations

from typing import Any

from wbcd_task1.execution.server.state_types import ArmState


class NeroInterfaceServerBackend:
    """Execution backend backed by the migrated Nero interface server."""

    def __init__(
        self,
        arms: list[str] | None = None,
        enable_gripper: bool = True,
        tcp_offset_enabled: bool = False,
        limit_z: float = 0.07,
        server_cls: type | None = None,
    ):
        self.arms = arms or ["right"]
        self.enable_gripper = bool(enable_gripper)
        self.tcp_offset_enabled = bool(tcp_offset_enabled)
        self.limit_z = float(limit_z)
        self._server_cls = server_cls
        self._server: Any | None = None
        self._connected = False
        self._enabled = {arm: False for arm in self.arms}

    def connect(self) -> None:
        if self._server is None:
            server_cls = self._server_cls
            if server_cls is None:
                from wbcd_task1.execution.server.nero_interface_server import NeroDualArmServer

                server_cls = NeroDualArmServer
            self._server = server_cls(
                gripper_enabled=self.enable_gripper,
                tcp_offset_enabled=self.tcp_offset_enabled,
                limit_z=self.limit_z,
            )
        self._connected = True
        for arm in self.arms:
            self._enabled[arm] = True

    def disconnect(self) -> None:
        if self._server is not None:
            for arm in self.arms:
                self.stop(arm)
            self._disconnect_robot_handles()
        self._connected = False
        for arm in self.arms:
            self._enabled[arm] = False

    def enable(self, arm: str | None = None) -> None:
        self._ensure_server()
        for selected_arm in self._selected_arms(arm):
            self._enabled[selected_arm] = True

    def stop(self, arm: str | None = None) -> None:
        server = self._ensure_server()
        for selected_arm in self._selected_arms(arm):
            server.robot_stop(self._server_arm(selected_arm))

    def reset(self, arm: str | None = None) -> None:
        server = self._ensure_server()
        for selected_arm in self._selected_arms(arm):
            robot = getattr(server, f"{selected_arm}_robot", None)
            if robot is not None and hasattr(robot, "reset"):
                robot.reset()
            self.go_home(selected_arm)

    def go_home(self, arm: str | None = None) -> None:
        server = self._ensure_server()
        selected = self._selected_arms(arm)
        if set(selected) == {"left", "right"} and hasattr(server, "robot_go_home"):
            server.robot_go_home()
            return
        for selected_arm in selected:
            getattr(server, f"{selected_arm}_robot_go_home")()

    def get_state(self, arm: str | None = None) -> dict[str, ArmState]:
        server = self._ensure_server()
        states: dict[str, ArmState] = {}
        for selected_arm in self._selected_arms(arm):
            gripper_state = self._gripper_state(server, selected_arm)
            states[selected_arm] = ArmState(
                arm=selected_arm,
                connected=self._connected,
                enabled=self._enabled.get(selected_arm, False),
                joints=self.get_joints(selected_arm),
                tcp_pose=self.get_tcp_pose(selected_arm),
                gripper_width_m=gripper_state.get("width"),
            )
        return states

    def get_tcp_pose(self, arm: str) -> list[float]:
        server = self._ensure_server()
        return list(getattr(server, f"{arm}_robot_get_ee_pose")())

    def get_joints(self, arm: str) -> list[float]:
        server = self._ensure_server()
        return list(getattr(server, f"{arm}_robot_get_joint_positions")())

    def move_j(self, arm: str, joints: list[float], delta: bool = False) -> None:
        server = self._ensure_server()
        getattr(server, f"{arm}_robot_move_to_joint_positions")(list(joints), bool(delta))

    def move_p(self, arm: str, pose: list[float], delta: bool = False) -> None:
        server = self._ensure_server()
        getattr(server, f"{arm}_robot_move_to_ee_pose")(list(pose), bool(delta))

    def servo_delta_pose(self, arm: str, delta_pose: list[float]) -> None:
        server = self._ensure_server()
        ok = server.servo_p_OL(self._server_arm(arm), list(delta_pose), True)
        if ok is False:
            raise RuntimeError(f"servo_p_OL failed for {arm}")

    def open_gripper(self, arm: str, width_m: float = 0.1, force: float = 1.0) -> None:
        server = self._ensure_server()
        ok = getattr(server, f"{arm}_gripper_goto")(float(width_m), float(force))
        if ok is False:
            raise RuntimeError(f"open gripper failed for {arm}")

    def close_gripper(self, arm: str, width_m: float = 0.0, force: float = 1.0) -> None:
        server = self._ensure_server()
        ok = getattr(server, f"{arm}_gripper_goto")(float(width_m), float(force))
        if ok is False:
            raise RuntimeError(f"close gripper failed for {arm}")

    def _ensure_server(self):
        if self._server is None:
            self.connect()
        return self._server

    def _selected_arms(self, arm: str | None) -> list[str]:
        if arm is None:
            return list(self.arms)
        if arm not in self.arms:
            raise ValueError(f"Unknown arm: {arm}")
        return [arm]

    @staticmethod
    def _server_arm(arm: str) -> str:
        return f"{arm}_robot"

    @staticmethod
    def _gripper_state(server, arm: str) -> dict:
        method = getattr(server, f"{arm}_gripper_get_state", None)
        if method is None:
            return {}
        state = method()
        return state if isinstance(state, dict) else {}

    def _disconnect_robot_handles(self) -> None:
        server = self._server
        for arm in self.arms:
            robot = getattr(server, f"{arm}_robot", None)
            if robot is not None and hasattr(robot, "disconnect"):
                robot.disconnect()

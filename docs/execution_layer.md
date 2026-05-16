# Execution Layer

The execution layer is robot-only. It exposes command types in
`src/wbcd_task1/execution/server/command_types.py`:

- connect, disconnect, enable, stop, reset, go_home;
- get_state, get_tcp_pose, get_joints;
- move_j, move_p, servo_delta_pose;
- open_gripper, close_gripper.

The layer is split into:

- `agilex_server.py`: zerorpc facade and dispatcher construction.
- `command_dispatcher.py`: maps command objects to backend methods.
- `safety_guard.py`: clamps servo delta pose and enforces simple TCP limits.
- `sdk/mock_backend.py`: no-hardware dry-run backend.
- `sdk/nero_sdk.py`: the only new main-code adapter that imports `pyAgxArm`.
- `kinematics/nero_solver.py`: Pinocchio-based IK; old analytic `Solver` is not
  migrated.

Execution must not import perception, planning, or tasks.

# External Execution Server

The real robot execution server is not part of this repository.

- Source: `https://github.com/Key-Zzs/agilex_teleop`
- Server file: `nero_interface/nero_interface_server.py`
- Default endpoint: `tcp://<robot_ip>:4242`

RPC methods used by this repository:

- `servo_p_OL(robot_arm, pose, delta)`
- `left_gripper_goto(width, force)`
- `right_gripper_goto(width, force)`
- Optional: `robot_stop(robot_arm)`, state query methods such as `left_robot_get_ee_pose()`

Example server startup on the execution machine:

```bash
python nero_interface/nero_interface_server.py --ip 0.0.0.0 --port 4242
```

Debug client connection from this repository:

```bash
python scripts/debug_comm.py --config configs/debug_comm.yaml
```

The debug script does not send motion by default. Use explicit flags:

```bash
python scripts/debug_comm.py --config configs/debug_comm.yaml --allow-motion
python scripts/debug_comm.py --config configs/debug_comm.yaml --allow-gripper
```

Safety note: `close()` in the new adapter only closes the socket. It does not call `robot_stop`. Use `emergency_stop()` explicitly when an emergency stop is intended.

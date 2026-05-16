# Code Migration Report

## Repository Scan

The expected top-level `agilex_teleop` package was not present as a directory.
The old package identity was found in `pyproject.toml`, and the functional code
was under:

- `nero/teleop/interface/nero_interface_server.py`
- `nero/teleop/interface/nero_interface_client.py`
- `nero/teleop/nero_dual_arm.py`
- `nero/teleop/nero_teleop_config.py`
- `nero/kinematics/analytic_IK_solver.py`
- `nero/kinematics/nero_kinematics/`
- `pyAgxArm/`

## Kept As Main Code

- New task package under `src/wbcd_task1/`.
- `pyAgxArm/` is retained in place as the hardware SDK dependency. The new
  execution layer references it only through
  `src/wbcd_task1/execution/sdk/nero_sdk.py`.

## Migrated Into New Main Code

| Old path | New path | Notes |
| --- | --- | --- |
| `nero/teleop/interface/nero_interface_server.py` | `src/wbcd_task1/execution/server/` and `src/wbcd_task1/execution/sdk/nero_sdk.py` | Server concerns split into command types, dispatcher, safety guard, RPC facade, and SDK adapter. |
| `nero/kinematics/analytic_IK_solver.py` | `src/wbcd_task1/execution/kinematics/nero_solver.py` | Only the Pinocchio solver API was migrated. The old analytic `Solver` class was not migrated. |
| `pyAgxArm/` SDK usage | `src/wbcd_task1/execution/sdk/nero_sdk.py` | SDK is referenced through a thin adapter rather than imported by planning or task code. |

## Moved To Legacy

The old `nero/` directory was moved to `legacy/nero/`.

This includes:

- client code;
- teleoperation code;
- LeRobot-facing robot wrapper/config;
- old server source retained for reference;
- old tests and hardware experiments;
- old analytic IK implementation and dependencies;
- notebooks and servo experiments.

## Suggested Deletes After Stabilization

- `legacy/nero/teleop/`
- `legacy/nero/tests/`
- old analytic IK dependencies under `legacy/nero/kinematics/nero_kinematics/`

These are kept for now because they may contain hardware-specific details useful
while validating the new execution adapter.

## Uncertain Files

- `pyAgxArm/demos/`: not part of WBCD task 1, but kept because it belongs to the
  retained SDK package and may be useful for hardware diagnosis.
- `README_pyAgxArm.md` and `docs/effector`, `docs/nero`: kept as SDK hardware
  documentation.

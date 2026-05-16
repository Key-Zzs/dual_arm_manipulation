# Architecture

This repository is now organized around WBCD task 1: grasp a test tube and
insert it into a rack using a traditional perception, planning, and control
pipeline.

Main package:

- `src/wbcd_task1/core`: config loading, result types, logging, exceptions.
- `src/wbcd_task1/execution`: robot-only execution layer. It owns RPC server,
  command dispatch, safety limits, SDK adapters, and kinematics.
- `src/wbcd_task1/perception`: cameras, OpenCV/YOLO/AprilTag adapters,
  perception result types, and calibration helpers.
- `src/wbcd_task1/planning`: state machine, rule checks, retry/recovery
  policies, motion helpers, and controllers.
- `src/wbcd_task1/tasks/wbcd_task1_tube_insert`: task context, state handlers,
  task orchestration, and the public `run_wbcd_task1` entry point.

Dependency direction:

`tasks -> planning -> execution/perception types`

`execution` does not import `perception`, `planning`, or `tasks`.

Configuration is task-level only. The repository intentionally does not create
`configs/execution`, `configs/perception`, `configs/calibration`, or
`configs/tasks`.

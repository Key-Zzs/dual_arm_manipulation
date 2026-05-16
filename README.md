# WBCD Task 1 Tube Insert

Traditional planning-control repository for WBCD task 1: grasp a test tube and
insert it into a test tube rack.

The main code is under `src/wbcd_task1/`:

- `execution`: Agilex Nero local execution service, SDK adapter, safety guard, and
  kinematics.
- `perception`: cameras, OpenCV/YOLO/AprilTag placeholders, result types, and
  calibration helpers.
- `planning`: state machine, rules, retry/recovery, controllers, and search
  patterns.
- `tasks/wbcd_task1_tube_insert`: complete task orchestration and entry point.

Run the dry-run task:

```bash
python scripts/run_wbcd_task1.py --config configs/wbcd_task1_dry_run.yaml --dry-run
```

Initialize the local execution service:

```bash
python scripts/start_execution_server.py --config configs/debug_execution.yaml --dry-run
```

Run tests:

```bash
pytest
```

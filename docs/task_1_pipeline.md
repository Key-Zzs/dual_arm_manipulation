# Task 1 Pipeline

Task 1 is organized as five stages:

1. `locate_tube`
   - Uses `tube_detector`.
   - Stores `ctx.tube_detection`.
   - Dry-run returns a mock tube detection.

2. `grasp_tube`
   - Uses `pose_planner.plan_tube_grasp_pose`.
   - Executes `grasp_controller.execute_grasp`.
   - Checks `success_checks.check_grasp_success`.

3. `locate_rack`
   - Uses `rack_detector`.
   - Stores `ctx.rack_detection`.
   - Dry-run returns a mock rack detection.

4. `locate_empty_hole`
   - Uses `hole_detector`.
   - Stores `ctx.hole_detection`.
   - Dry-run returns a mock hole detection.

5. `insert_tube`
   - Uses `pose_planner.plan_insertion_pose`.
   - Executes `insertion_controller.execute_insertion`.
   - Checks `success_checks.check_insert_success`.

Each stage returns `StageResult`. `run_task_1` aggregates these into `TaskResult` and retries failed stages according to config.

# WBCD Task 1 Pipeline

Task entry point:

`src/wbcd_task1/tasks/wbcd_task1_tube_insert/main.py`

Public API:

```python
def run_wbcd_task1(config_path: str, dry_run: bool = False) -> TaskResult:
    ...
```

State sequence:

1. initialize
2. locate_tube
3. align_to_tube
4. grasp_tube
5. verify_grasp
6. locate_rack
7. locate_empty_hole
8. align_to_hole
9. insert_tube
10. verify_insertion

Dry-run uses the mock execution backend and mock observations, so it can run the
full state machine without a robot or cameras.

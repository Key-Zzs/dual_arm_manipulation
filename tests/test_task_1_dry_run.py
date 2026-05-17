from __future__ import annotations
from bimanual_rule_control.tasks.main import run


def test_task_1_dry_run_success():
    result = run("configs/dry_run.yaml", task_name="task_1", dry_run=True)
    assert result.success
    assert [stage.stage_name for stage in result.stage_results] == [
        "locate_tube",
        "grasp_tube",
        "locate_rack",
        "locate_empty_hole",
        "insert_tube",
    ]

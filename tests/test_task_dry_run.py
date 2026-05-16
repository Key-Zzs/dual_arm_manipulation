from wbcd_task1.tasks.wbcd_task1_tube_insert.main import run_wbcd_task1


def test_task_dry_run_runs_full_state_machine():
    result = run_wbcd_task1("configs/wbcd_task1_dry_run.yaml", dry_run=True)
    assert result.ok
    assert len(result.states) == 10
    assert [state.name for state in result.states][0] == "initialize"
    assert [state.name for state in result.states][-1] == "verify_insertion"

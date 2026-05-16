from wbcd_task1.core.result import StateResult, TaskResult, TaskStatus
from wbcd_task1.planning.state_machine import StateMachine, StateSpec


class Context:
    dry_run = True
    config = {"states": {"flaky": {"enabled": True, "max_retries": 2}}}


def test_state_machine_retries_until_success():
    calls = {"count": 0}

    def flaky(_context):
        calls["count"] += 1
        if calls["count"] == 1:
            return StateResult("flaky", TaskStatus.FAILED, "first failure")
        return StateResult("flaky", TaskStatus.SUCCESS, "ok")

    result = TaskResult("test", TaskStatus.FAILED, dry_run=True)
    out = StateMachine([StateSpec("flaky", flaky)]).run(Context(), result)
    assert out.ok
    assert calls["count"] == 2
    assert out.states[0].attempts == 2

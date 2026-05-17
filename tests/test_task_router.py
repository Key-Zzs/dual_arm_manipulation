from __future__ import annotations
import pytest

from bimanual_rule_control.comm.mock_client import MockRobotClient
from bimanual_rule_control.core.context import TaskContext
from bimanual_rule_control.tasks.task_router import run_task


def test_task_1_routes():
    ctx = TaskContext(config={"task": {"dry_run": True}}, dry_run=True, robot_client=MockRobotClient())
    result = run_task("task_1", ctx)
    assert result.task_name == "task_1"


def test_unknown_task_raises():
    ctx = TaskContext(config={}, dry_run=True, robot_client=MockRobotClient())
    with pytest.raises(ValueError):
        run_task("missing", ctx)

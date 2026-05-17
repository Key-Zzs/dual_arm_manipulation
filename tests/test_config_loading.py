from __future__ import annotations
from bimanual_rule_control.core.config import load_config


def test_load_dry_run_config():
    cfg = load_config("configs/dry_run.yaml")
    assert cfg["task"]["dry_run"] is True
    assert cfg["comm"]["type"] == "mock"


def test_load_task_1_config():
    cfg = load_config("configs/task_1.yaml")
    assert cfg["task"]["name"] == "task_1"
    assert cfg["comm"]["robot_port"] == 4242

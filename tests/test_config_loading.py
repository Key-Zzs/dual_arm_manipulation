from pathlib import Path

from wbcd_task1.core.config import load_task_config


def test_task_config_loading_has_expected_sections():
    config = load_task_config(Path("configs/wbcd_task1_tube_insert.yaml"))
    assert set(["task", "execution", "perception", "calibration", "planning", "states"]).issubset(config)
    assert config["task"]["name"] == "wbcd_task1_tube_insert"


def test_dry_run_override():
    config = load_task_config(Path("configs/wbcd_task1_tube_insert.yaml"), dry_run=True)
    assert config["task"]["dry_run"] is True

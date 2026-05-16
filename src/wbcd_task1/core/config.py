"""Task-level YAML configuration loading."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from wbcd_task1.core.exceptions import ConfigError

REQUIRED_TASK_KEYS = ("task",)
FORBIDDEN_CONFIG_DIRS = (
    Path("configs/execution"),
    Path("configs/perception"),
    Path("configs/calibration"),
    Path("configs/tasks"),
)


def load_yaml(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file does not exist: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ConfigError(f"Config root must be a mapping: {config_path}")
    return data


def load_task_config(path: str | Path, *, dry_run: bool | None = None) -> dict[str, Any]:
    data = load_yaml(path)
    for key in REQUIRED_TASK_KEYS:
        if key not in data:
            raise ConfigError(f"Missing required config section: {key}")
    task = data.setdefault("task", {})
    if dry_run is not None:
        task["dry_run"] = bool(dry_run)
    return data


def get_path(config: dict[str, Any], dotted_key: str, default: Any = None) -> Any:
    current: Any = config
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result

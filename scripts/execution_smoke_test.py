#!/usr/bin/env python3
"""Smoke test the in-process execution dispatcher."""

from __future__ import annotations

import argparse

from _bootstrap import bootstrap

ROOT = bootstrap()

from wbcd_task1.core.config import load_task_config
from wbcd_task1.execution.server.agilex_server import build_dispatcher
from wbcd_task1.execution.server.command_types import ExecutionCommand, ExecutionCommandType


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs" / "debug_execution.yaml"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = load_task_config(args.config, dry_run=True if args.dry_run else None)
    dispatcher = build_dispatcher(config, dry_run=True)
    for command in [
        ExecutionCommand(ExecutionCommandType.CONNECT),
        ExecutionCommand(ExecutionCommandType.ENABLE, arm="right"),
        ExecutionCommand(ExecutionCommandType.GO_HOME, arm="right"),
        ExecutionCommand(ExecutionCommandType.GET_STATE, arm="right"),
    ]:
        response = dispatcher.dispatch(command)
        print(f"{command.command_type.value}: {response.status.value}")
        if not response.ok:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

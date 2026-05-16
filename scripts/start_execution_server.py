#!/usr/bin/env python3
"""Initialize the local execution service."""

from __future__ import annotations

import argparse

from _bootstrap import bootstrap

ROOT = bootstrap()

from wbcd_task1.core.config import load_task_config
from wbcd_task1.core.logger import configure_logging
from wbcd_task1.execution.server.agilex_server import create_execution_service


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs" / "debug_execution.yaml"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--connect", action="store_true", help="Connect hardware immediately after creating the service.")
    args = parser.parse_args()
    configure_logging()
    config = load_task_config(args.config, dry_run=True if args.dry_run else None)
    dry_run = bool(config.get("task", {}).get("dry_run", False))
    service = create_execution_service(config, dry_run=dry_run)
    print(f"Local execution service created (dry_run={dry_run}). No network endpoint is started.")
    if args.connect:
        response = service.connect()
        print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

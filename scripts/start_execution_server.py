#!/usr/bin/env python3
"""Start the execution RPC server."""

from __future__ import annotations

import argparse

from _bootstrap import bootstrap

ROOT = bootstrap()

from wbcd_task1.core.config import get_path, load_task_config
from wbcd_task1.core.logger import configure_logging
from wbcd_task1.execution.server.agilex_server import start_server


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs" / "debug_execution.yaml"))
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    configure_logging()
    config = load_task_config(args.config, dry_run=True if args.dry_run else None)
    host = args.host or str(get_path(config, "execution.server.host", "127.0.0.1"))
    port = args.port or int(get_path(config, "execution.server.port", 5000))
    print(f"Starting execution server on tcp://{host}:{port}")
    start_server(config, host=host, port=port, dry_run=bool(get_path(config, "task.dry_run", False)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
from __future__ import annotations
"""Debug the external Nero ZeroRPC communication path."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bimanual_rule_control.comm.nero_comm_adapter import NeroCommAdapter
from bimanual_rule_control.core.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/debug_comm.yaml")
    parser.add_argument("--allow-motion", action="store_true")
    parser.add_argument("--allow-gripper", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.allow_motion:
        config.setdefault("comm", {})["debug"] = False
    client = NeroCommAdapter(config, dry_run=False)
    try:
        print("Connecting to external Nero execution server...")
        client.connect()
        print("Connected.")
        if args.allow_motion:
            result = client.send_arm_delta_pose("right", [0, 0, 0, 0, 0, 0])
            print(f"motion: success={result.success} message={result.message}")
        else:
            print("Motion command skipped. Pass --allow-motion to send one.")
        if args.allow_gripper:
            result = client.handle_gripper("right", 1.0)
            print(f"gripper: success={result.success} message={result.message}")
        else:
            print("Gripper command skipped. Pass --allow-gripper to send one.")
    except RuntimeError as exc:
        print(f"Communication debug failed: {exc}")
        raise SystemExit(2) from exc
    finally:
        client.close()


if __name__ == "__main__":
    main()

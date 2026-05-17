# Bimanual Rule Control

Lightweight traditional perception, planning, and communication stack for dual-arm rule-based manipulation.

This repository does not contain the real robot execution server or Nero SDK control layer. Runtime robot execution is delegated to the external `agilex_teleop` zerorpc server, while this project keeps perception, planning, task orchestration, and a thin communication adapter.

## Architecture

```text
perception -> planning/tasks -> comm adapter -> dual_agilex_nero -> external agilex_teleop server
```

The preserved communication interface lives in:

```text
src/bimanual_rule_control/comm/dual_agilex_nero/
```

The four files in that directory are intentionally kept as the verified robot communication interface.

## Dry Run

```bash
python scripts/dry_run_task_1.py
python scripts/run_task.py --config configs/dry_run.yaml --task task_1 --dry-run
```

## Tests

```bash
/home/keyz/miniconda3/envs/lerobot/bin/pytest tests
```

If `pytest` is available in your active environment:

```bash
pytest tests
```

## Optional Real Communication

Start the external server from `Key-Zzs/agilex_teleop` first, then install the optional RPC dependency and run the communication debug script:

```bash
pip install -e ".[rpc]"
python scripts/debug_comm.py --config configs/debug_comm.yaml
```

Motion and gripper commands are gated by explicit flags:

```bash
python scripts/debug_comm.py --config configs/debug_comm.yaml --allow-motion
python scripts/debug_comm.py --config configs/debug_comm.yaml --allow-gripper
```

`close()` in the new adapter only releases the client/socket path. Emergency stop is exposed separately as `emergency_stop()`.

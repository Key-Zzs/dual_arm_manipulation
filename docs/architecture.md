# Architecture

```text
perception -> planning/tasks -> comm adapter -> dual_agilex_nero -> external agilex_teleop server
```

This repository is now structured as a lightweight traditional rule-control stack. It does not contain the real robot execution server and does not call the Nero SDK directly.

The execution layer remains external:

- Repository: `https://github.com/Key-Zzs/agilex_teleop`
- Server file: `nero_interface/nero_interface_server.py`
- Transport: zerorpc, usually on port `4242`

The preserved `src/bimanual_rule_control/comm/dual_agilex_nero/` package is the verified communication interface. The new `NeroCommAdapter` wraps that interface so planning and task code do not import zerorpc or depend on RPC method details.

Perception and planning are intentionally decoupled from the real server. Dry-run uses mock cameras, mock detectors, and `MockRobotClient`.

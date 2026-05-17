# Cleanup Report

## 1. Cleanup Goal

本轮目标是把工作区清理为轻量传统规控仓库：主代码只保留 `bimanual_rule_control` 的 core / comm / perception / planning / tasks 架构，真实机器人执行层仍由外部 `agilex_teleop` zerorpc server 提供。

清理原则：

- 保留 `src/bimanual_rule_control/` 主包。
- 完整保留已验证通信接口 `src/bimanual_rule_control/comm/dual_agilex_nero/` 四个文件。
- 移除主代码路径中的 LeRobot、teleop、dataset、training、policy、Oculus、DAgger、HuggingFace、W&B 等旧工程内容。
- 保证 dry-run 和新项目测试继续通过。

## 2. Kept Files

| 路径 | 保留原因 |
|---|---|
| `src/bimanual_rule_control/` | 新轻量规控主包。 |
| `src/bimanual_rule_control/comm/dual_agilex_nero/` | 已验证的 Nero zerorpc 通信接口，按要求完整保留。 |
| `configs/task_1.yaml` | task_1 真实/默认配置。 |
| `configs/dry_run.yaml` | dry-run 测试配置。 |
| `configs/debug_comm.yaml` | 外部 zerorpc 通信调试配置。 |
| `configs/debug_perception.yaml` | 感知调试配置骨架。 |
| `scripts/run_task.py` | 通用任务运行入口。 |
| `scripts/dry_run_task_1.py` | task_1 dry-run 快速入口。 |
| `scripts/debug_comm.py` | 安全调试外部通信，不默认发运动命令。 |
| `scripts/debug_camera.py` | 相机调试入口骨架。 |
| `scripts/debug_perception.py` | 感知调试入口骨架。 |
| `tests/test_config_loading.py` | 新配置加载测试。 |
| `tests/test_mock_client.py` | dry-run mock robot client 测试。 |
| `tests/test_nero_comm_adapter.py` | Nero adapter action/gripper 映射测试。 |
| `tests/test_task_router.py` | task router 测试。 |
| `tests/test_task_1_dry_run.py` | task_1 dry-run 流程测试。 |
| `tests/conftest.py` | 新项目测试的最小 `src` 路径配置。 |
| `docs/architecture.md` | 新架构说明。 |
| `docs/external_execution_server.md` | 外部执行 server 说明。 |
| `docs/task_1_pipeline.md` | task_1 阶段说明。 |
| `docs/migration_report.md` | Round 1 / Round 2 迁移分析记录。 |
| `README.md` | 已清理为当前轻量项目说明。 |
| `pyproject.toml` | 已清理为当前轻量项目依赖和包配置。 |
| `.gitignore` | 已补充 Python cache / build / env 忽略项。 |
| `LICENSE` | 项目许可证。 |

## 3. Deleted Files

本轮没有直接删除旧工程源码；出于可恢复性，旧源码和旧测试被移动到 `legacy/cleanup_2026_05_18/`。

已删除的内容仅限生成缓存：

- `.pytest_cache/`
- `src/bimanual_rule_control/**/__pycache__/`
- `tests/**/__pycache__/`
- `legacy/cleanup_2026_05_18/**/__pycache__/`

## 4. Moved to Legacy

旧工程内容已移到 `legacy/cleanup_2026_05_18/`，主代码、scripts、tests、pyproject 均不依赖该目录。

| 原路径 | 新路径 | 原因 |
|---|---|---|
| `src/lerobot/` | `legacy/cleanup_2026_05_18/lerobot/` | LeRobot 框架本体，不属于轻量规控主包。 |
| `dual_arm_data_collection/` | `legacy/cleanup_2026_05_18/dual_arm_data_collection/` | 原完整 dual_arm_teleop 工程；已将 `dual_agilex_nero` 四文件迁入主包。 |
| `examples/` | `legacy/cleanup_2026_05_18/examples/` | LeRobot 示例、dataset/training/teleop 示例。 |
| `benchmarks/` | `legacy/cleanup_2026_05_18/benchmarks/` | LeRobot 视频 benchmark，与当前任务无关。 |
| `docker/` | `legacy/cleanup_2026_05_18/docker/` | 旧 LeRobot Docker 文件，不作为当前安装路径。 |
| `media/` | `legacy/cleanup_2026_05_18/media/` | 旧 LeRobot 图片和 W&B 媒体资源。 |
| `docs/source/` | `legacy/cleanup_2026_05_18/docs/source/` | LeRobot 文档源。 |
| `docs/README.md` | `legacy/cleanup_2026_05_18/docs/README.md` | 旧文档入口。 |
| `tests/artifacts/` | `legacy/cleanup_2026_05_18/tests/artifacts/` | 旧 dataset/policy 测试 artifact。 |
| `tests/async_inference/` | `legacy/cleanup_2026_05_18/tests/async_inference/` | 旧异步推理测试。 |
| `tests/cameras/` | `legacy/cleanup_2026_05_18/tests/cameras/` | 旧 LeRobot 相机测试。 |
| `tests/datasets/` | `legacy/cleanup_2026_05_18/tests/datasets/` | 旧 dataset 测试。 |
| `tests/policies/` | `legacy/cleanup_2026_05_18/tests/policies/` | 旧 policy 测试。 |
| `tests/processor/` | `legacy/cleanup_2026_05_18/tests/processor/` | 旧 processor 测试。 |
| `tests/rl/` | `legacy/cleanup_2026_05_18/tests/rl/` | 旧 RL 测试。 |
| `tests/robots/` | `legacy/cleanup_2026_05_18/tests/robots/` | 旧 LeRobot robot 测试。 |
| `tests/teleoperators/` | `legacy/cleanup_2026_05_18/tests/teleoperators/` | 旧 teleop 测试。 |
| `tests/training/` | `legacy/cleanup_2026_05_18/tests/training/` | 旧训练测试。 |
| `tests/transport/` | `legacy/cleanup_2026_05_18/tests/transport/` | 旧 transport 测试。 |
| `tests/utils/`, `tests/utils.py` | `legacy/cleanup_2026_05_18/tests/` | 旧测试工具。 |
| `tests/test_available.py` | `legacy/cleanup_2026_05_18/tests/test_available.py` | 旧 LeRobot 测试。 |
| `tests/test_control_robot.py` | `legacy/cleanup_2026_05_18/tests/test_control_robot.py` | 旧 LeRobot robot 控制测试。 |
| `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `Makefile`, `README_lerobot.md` | `legacy/cleanup_2026_05_18/` | 旧 LeRobot 项目元文件。 |
| `requirements*.txt`, `requirements.in`, `docs-requirements.txt` | `legacy/cleanup_2026_05_18/` | 旧依赖入口，避免误导安装。 |
| `rm_tmp.sh` | `legacy/cleanup_2026_05_18/rm_tmp.sh` | 旧临时清理脚本，主项目不需要。 |

## 5. Dependency Cleanup

`pyproject.toml` 已保留轻量项目配置：

- 包名：`bimanual-rule-control`
- Python：`>=3.10`
- 默认依赖：
  - `numpy`
  - `PyYAML`

optional extras：

- `rpc`: `zerorpc`
- `vision`: `opencv-python`
- `yolo`: `ultralytics`
- `realsense`: `pyrealsense2`
- `apriltag`: `pupil-apriltags`
- `dev`: `pytest>=8.1.0`

已从主依赖中移除或不再引入：

- LeRobot
- torch / torchvision
- datasets / huggingface_hub
- wandb
- diffusers / transformers
- policy / training / RL 栈
- Oculus / teleop 相关依赖
- pyAgxArm / Nero SDK / IK solver

真实执行层仍由外部 `agilex_teleop` server 负责，因此当前仓库不安装机器人 SDK 依赖。

## 6. Import Audit

主运行路径扫描范围：

```bash
src/bimanual_rule_control scripts tests configs README.md pyproject.toml
```

结果：

- `import lerobot|from lerobot`
  - 仅存在于：
    - `src/bimanual_rule_control/comm/dual_agilex_nero/config_nero.py`
    - `src/bimanual_rule_control/comm/dual_agilex_nero/nero_dual_arm.py`
  - 保留原因：这是已验证通信接口的 LeRobot 兼容路径，并且已被 `try/except` optional fallback 包住；dry-run 和 tests 不依赖 LeRobot。
- `dual_arm_teleop`
  - 主代码仅在 `config_nero.py` 注释中出现，用于说明兼容来源。
  - `docs/migration_report.md` 中保留历史路径记录。
- `import torch|from torch`
  - 主运行路径无命中。
- `wandb|huggingface|datasets`
  - 主运行路径无命中。
  - `docs/migration_report.md` 中有历史依赖分析文本命中，非运行依赖。

`legacy/cleanup_2026_05_18/` 中仍包含旧 LeRobot 源码和测试，可能有大量历史 import；该目录不被主代码、scripts、tests、pyproject 引用。

## 7. Validation

清理后验证结果：

```bash
/home/keyz/miniconda3/envs/lerobot/bin/pytest tests
```

结果：

```text
9 passed in 0.18s
```

```bash
python scripts/dry_run_task_1.py
```

结果：`task_1` 成功，包含 `locate_tube`、`grasp_tube`、`locate_rack`、`locate_empty_hole`、`insert_tube` 五个成功阶段。

```bash
python scripts/run_task.py --config configs/dry_run.yaml --task task_1 --dry-run
```

结果：`task_1` 成功，五个阶段全部通过。

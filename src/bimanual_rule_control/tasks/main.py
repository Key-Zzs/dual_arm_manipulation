from __future__ import annotations
"""Task runtime entrypoint."""

from bimanual_rule_control.comm.mock_client import MockRobotClient
from bimanual_rule_control.comm.nero_comm_adapter import NeroCommAdapter
from bimanual_rule_control.core.config import load_config
from bimanual_rule_control.core.context import TaskContext
from bimanual_rule_control.core.result import TaskResult
from bimanual_rule_control.perception.base import MockDetector
from bimanual_rule_control.perception.cameras.camera_manager import CameraManager
from bimanual_rule_control.perception.cameras.mock_camera import MockCamera
from bimanual_rule_control.perception.opencv.hole_detector import OpenCVHoleDetector
from bimanual_rule_control.perception.opencv.rack_detector import OpenCVRackDetector
from bimanual_rule_control.perception.opencv.tube_detector import OpenCVTubeDetector
from bimanual_rule_control.tasks.task_router import run_task


def _build_robot_client(config: dict, dry_run: bool):
    comm_type = str(config.get("comm", {}).get("type", "mock" if dry_run else "nero_comm_adapter"))
    if dry_run or comm_type == "mock":
        return MockRobotClient()
    return NeroCommAdapter(config, dry_run=False)


def _build_camera_manager(config: dict, dry_run: bool) -> CameraManager | None:
    if dry_run:
        return CameraManager({"wrist": MockCamera("wrist"), "head": MockCamera("head")})
    return None


def _build_detectors(dry_run: bool):
    if dry_run:
        return {
            "tube_detector": MockDetector("tube"),
            "rack_detector": MockDetector("rack"),
            "hole_detector": MockDetector("hole"),
            "tag_detector": MockDetector("apriltag"),
        }
    return {
        "tube_detector": OpenCVTubeDetector(),
        "rack_detector": OpenCVRackDetector(),
        "hole_detector": OpenCVHoleDetector(),
        "tag_detector": None,
    }


def run(config_path: str, task_name: str = "task_1", dry_run: bool = False) -> TaskResult:
    config = load_config(config_path)
    config_dry_run = bool(config.get("task", {}).get("dry_run", False))
    effective_dry_run = bool(dry_run or config_dry_run)
    config.setdefault("task", {})["dry_run"] = effective_dry_run

    robot_client = _build_robot_client(config, effective_dry_run)
    camera_manager = _build_camera_manager(config, effective_dry_run)
    detectors = _build_detectors(effective_dry_run)
    ctx = TaskContext(
        config=config,
        dry_run=effective_dry_run,
        robot_client=robot_client,
        camera_manager=camera_manager,
        current_arm=str(config.get("task", {}).get("default_arm", "right")),
        **detectors,
    )

    try:
        robot_client.connect()
        if camera_manager is not None:
            camera_manager.open()
        return run_task(task_name, ctx)
    finally:
        if camera_manager is not None:
            camera_manager.close()
        robot_client.close()

from __future__ import annotations
"""Task 1 pipeline: locate, grasp, locate rack/hole, insert."""

from collections.abc import Callable

from bimanual_rule_control.core.context import TaskContext
from bimanual_rule_control.core.result import StageResult, TaskResult
from bimanual_rule_control.perception.result_types import DetectionResult, HoleDetection, RackDetection, TubeDetection
from bimanual_rule_control.planning import pose_planner, success_checks
from bimanual_rule_control.planning.controllers.grasp_controller import execute_grasp
from bimanual_rule_control.planning.controllers.insertion_controller import execute_insertion
from bimanual_rule_control.planning.retry_policy import record_retry, should_retry
from bimanual_rule_control.planning.task_stage import (
    STAGE_GRASP_TUBE,
    STAGE_INSERT_TUBE,
    STAGE_LOCATE_EMPTY_HOLE,
    STAGE_LOCATE_RACK,
    STAGE_LOCATE_TUBE,
    TASK_1_STAGES,
)


def _mock_detection(stage_name: str) -> DetectionResult:
    if stage_name == STAGE_LOCATE_TUBE:
        return DetectionResult(True, "mock tube detected", TubeDetection("mock_tube", 1.0, [0, 0, 0, 0, 0, 0]))
    if stage_name == STAGE_LOCATE_RACK:
        return DetectionResult(True, "mock rack detected", RackDetection("mock_rack", 1.0, [0, 0, 0, 0, 0, 0]))
    return DetectionResult(True, "mock hole detected", HoleDetection("mock_hole", 1.0, [0, 0, 0, 0, 0, 0]))


def locate_tube(ctx: TaskContext) -> StageResult:
    result = ctx.tube_detector.detect(None) if ctx.tube_detector is not None else _mock_detection(STAGE_LOCATE_TUBE)
    if result.success:
        ctx.tube_detection = result.data
    ok = result.success and success_checks.check_tube_detected(ctx)
    return StageResult(STAGE_LOCATE_TUBE, ok, result.message, {"detection": result.data})


def grasp_tube(ctx: TaskContext) -> StageResult:
    pose_delta = pose_planner.plan_tube_grasp_pose(ctx)
    ctx.target_pose = pose_delta
    command = execute_grasp(ctx, pose_delta, arm=ctx.current_arm)
    ok = command.success and success_checks.check_grasp_success(ctx)
    return StageResult(STAGE_GRASP_TUBE, ok, command.message, {"pose_delta": pose_delta})


def locate_rack(ctx: TaskContext) -> StageResult:
    result = ctx.rack_detector.detect(None) if ctx.rack_detector is not None else _mock_detection(STAGE_LOCATE_RACK)
    if result.success:
        ctx.rack_detection = result.data
    ok = result.success and success_checks.check_rack_detected(ctx)
    return StageResult(STAGE_LOCATE_RACK, ok, result.message, {"detection": result.data})


def locate_empty_hole(ctx: TaskContext) -> StageResult:
    result = ctx.hole_detector.detect(None) if ctx.hole_detector is not None else _mock_detection(STAGE_LOCATE_EMPTY_HOLE)
    if result.success:
        ctx.hole_detection = result.data
    ok = result.success and success_checks.check_hole_detected(ctx)
    return StageResult(STAGE_LOCATE_EMPTY_HOLE, ok, result.message, {"detection": result.data})


def insert_tube(ctx: TaskContext) -> StageResult:
    pose_delta = pose_planner.plan_insertion_pose(ctx)
    ctx.target_pose = pose_delta
    command = execute_insertion(ctx, pose_delta, arm=ctx.current_arm)
    ok = command.success and success_checks.check_insert_success(ctx)
    return StageResult(STAGE_INSERT_TUBE, ok, command.message, {"pose_delta": pose_delta})


STAGE_FUNCTIONS: dict[str, Callable[[TaskContext], StageResult]] = {
    STAGE_LOCATE_TUBE: locate_tube,
    STAGE_GRASP_TUBE: grasp_tube,
    STAGE_LOCATE_RACK: locate_rack,
    STAGE_LOCATE_EMPTY_HOLE: locate_empty_hole,
    STAGE_INSERT_TUBE: insert_tube,
}


def _run_stage_with_retries(ctx: TaskContext, stage_name: str) -> StageResult:
    stage_fn = STAGE_FUNCTIONS[stage_name]
    while True:
        result = stage_fn(ctx)
        if result.success:
            return result
        if not should_retry(ctx, stage_name):
            return result
        attempt = record_retry(ctx, stage_name)
        result.message = f"{result.message}; retry {attempt}"


def run_task_1(ctx: TaskContext) -> TaskResult:
    ctx.current_arm = str(ctx.config.get("task", {}).get("default_arm", ctx.current_arm))
    stage_results: list[StageResult] = []
    for stage_name in TASK_1_STAGES:
        if not ctx.config.get("stages", {}).get(stage_name, {}).get("enabled", True):
            stage_results.append(StageResult(stage_name, True, "stage disabled"))
            continue
        result = _run_stage_with_retries(ctx, stage_name)
        stage_results.append(result)
        if not result.success:
            return TaskResult("task_1", False, f"stage failed: {stage_name}", stage_results)
    return TaskResult("task_1", True, "task_1 completed", stage_results)

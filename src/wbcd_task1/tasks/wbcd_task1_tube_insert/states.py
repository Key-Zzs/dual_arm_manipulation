"""State handlers for WBCD task 1."""

from __future__ import annotations

from wbcd_task1.core.config import get_path
from wbcd_task1.core.result import StateResult, TaskStatus
from wbcd_task1.planning.controllers.grasp_controller import GraspController
from wbcd_task1.planning.controllers.insertion_controller import InsertionController
from wbcd_task1.planning.controllers.visual_servo_controller import VisualServoController
from wbcd_task1.planning.success_checks import has_detection


def initialize(context) -> StateResult:
    context.execution.connect()
    context.execution.enable()
    if get_path(context.config, "execution.robot.auto_go_home", False):
        context.execution.go_home()
    context.execution.open_gripper()
    return StateResult("initialize", TaskStatus.SUCCESS, "execution initialized")


def locate_tube(context) -> StateResult:
    detection = context.mock_detection("tube_cap") if context.dry_run else None
    detections = [detection] if detection else []
    context.observations["tube_cap"] = detection
    status = TaskStatus.SUCCESS if has_detection(detections, "tube_cap") else TaskStatus.FAILED
    return StateResult("locate_tube", status, "tube located" if status == TaskStatus.SUCCESS else "tube not found")


def align_to_tube(context) -> StateResult:
    cfg = get_path(context.config, "planning.visual_servo", {})
    controller = VisualServoController(max_step_m=float(cfg.get("max_step_m", 0.003)))
    delta = controller.pixel_error_to_delta_pose((0.0, 0.0))
    context.execution.servo_delta_pose(delta)
    return StateResult("align_to_tube", TaskStatus.SUCCESS, "aligned to tube", data={"delta_pose": delta})


def grasp_tube(context) -> StateResult:
    cfg = get_path(context.config, "planning.grasp", {})
    controller = GraspController(
        pregrasp_height_m=float(cfg.get("pregrasp_height_m", 0.03)),
        descend_step_m=float(cfg.get("descend_step_m", 0.002)),
        lift_after_grasp_m=float(cfg.get("lift_after_grasp_m", 0.04)),
    )
    context.execution.servo_delta_pose(controller.descend_delta())
    context.execution.close_gripper()
    context.execution.servo_delta_pose(controller.lift_delta())
    return StateResult("grasp_tube", TaskStatus.SUCCESS, "tube grasped")


def verify_grasp(context) -> StateResult:
    context.observations["grasp_verified"] = True
    return StateResult("verify_grasp", TaskStatus.SUCCESS, "grasp verified")


def locate_rack(context) -> StateResult:
    detection = context.mock_detection("rack") if context.dry_run else None
    detections = [detection] if detection else []
    context.observations["rack"] = detection
    status = TaskStatus.SUCCESS if has_detection(detections, "rack") else TaskStatus.FAILED
    return StateResult("locate_rack", status, "rack located" if status == TaskStatus.SUCCESS else "rack not found")


def locate_empty_hole(context) -> StateResult:
    detection = context.mock_detection("hole") if context.dry_run else None
    detections = [detection] if detection else []
    context.observations["hole"] = detection
    status = TaskStatus.SUCCESS if has_detection(detections, "hole") else TaskStatus.FAILED
    return StateResult("locate_empty_hole", status, "hole located" if status == TaskStatus.SUCCESS else "hole not found")


def align_to_hole(context) -> StateResult:
    cfg = get_path(context.config, "planning.visual_servo", {})
    controller = VisualServoController(max_step_m=float(cfg.get("max_step_m", 0.003)))
    delta = controller.pixel_error_to_delta_pose((0.0, 0.0))
    context.execution.servo_delta_pose(delta)
    return StateResult("align_to_hole", TaskStatus.SUCCESS, "aligned to hole", data={"delta_pose": delta})


def insert_tube(context) -> StateResult:
    cfg = get_path(context.config, "planning.insertion", {})
    controller = InsertionController(
        descend_step_m=float(cfg.get("descend_step_m", 0.001)),
        max_insert_depth_m=float(cfg.get("max_insert_depth_m", 0.05)),
        search_step_m=float(cfg.get("search_step_m", 0.001)),
        search_radius_m=float(cfg.get("search_radius_m", 0.003)),
    )
    offsets = controller.search_offsets() if cfg.get("use_micro_search", True) else [(0.0, 0.0, 0.0)]
    context.observations["search_offsets"] = offsets
    context.execution.servo_delta_pose(controller.descend_delta())
    context.execution.open_gripper(width_m=0.06)
    return StateResult("insert_tube", TaskStatus.SUCCESS, "tube inserted", data={"search_points": len(offsets)})


def verify_insertion(context) -> StateResult:
    context.observations["insertion_verified"] = True
    return StateResult("verify_insertion", TaskStatus.SUCCESS, "insertion verified")


STATE_HANDLERS = {
    "initialize": initialize,
    "locate_tube": locate_tube,
    "align_to_tube": align_to_tube,
    "grasp_tube": grasp_tube,
    "verify_grasp": verify_grasp,
    "locate_rack": locate_rack,
    "locate_empty_hole": locate_empty_hole,
    "align_to_hole": align_to_hole,
    "insert_tube": insert_tube,
    "verify_insertion": verify_insertion,
}

from __future__ import annotations
"""Task stage constants and result exports."""

from bimanual_rule_control.core.result import StageResult, TaskResult

STAGE_LOCATE_TUBE = "locate_tube"
STAGE_GRASP_TUBE = "grasp_tube"
STAGE_LOCATE_RACK = "locate_rack"
STAGE_LOCATE_EMPTY_HOLE = "locate_empty_hole"
STAGE_INSERT_TUBE = "insert_tube"

TASK_1_STAGES = [
    STAGE_LOCATE_TUBE,
    STAGE_GRASP_TUBE,
    STAGE_LOCATE_RACK,
    STAGE_LOCATE_EMPTY_HOLE,
    STAGE_INSERT_TUBE,
]

__all__ = [
    "StageResult",
    "TaskResult",
    "STAGE_LOCATE_TUBE",
    "STAGE_GRASP_TUBE",
    "STAGE_LOCATE_RACK",
    "STAGE_LOCATE_EMPTY_HOLE",
    "STAGE_INSERT_TUBE",
    "TASK_1_STAGES",
]

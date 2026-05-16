"""Pinocchio-based Nero IK solver.

The old analytic ``Solver`` class is intentionally not migrated. This module
keeps only the Pinocchio DLS solver API needed by the execution layer.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np

from wbcd_task1.execution.kinematics.transforms import matrix_to_rpy, pose6_to_matrix

try:
    import pinocchio as pin
except ImportError:  # pragma: no cover
    pin = None


@dataclass
class ContinuityRuntimeState:
    q_prev: np.ndarray
    q_prev2: np.ndarray | None = None
    theta0_prev: float | None = None
    q_lock: np.ndarray | None = None


class PinocchioSolver:
    """Iterative damped-least-squares IK solver for Nero."""

    def __init__(
        self,
        joint_limits,
        dt,
        n_psi=61,
        urdf_path=None,
        ee_frame_name="link7",
        tcp_offset=None,
        max_iterations=60,
        damping=1e-4,
        tol_pos=1e-4,
        tol_rot=5e-3,
    ):
        if pin is None:
            raise RuntimeError("Pinocchio is required for PinocchioSolver")

        self.joint_limits = list(joint_limits)
        self.dt = float(dt)
        self.n_psi = n_psi
        self.max_iterations = int(max_iterations)
        self.damping = float(damping)
        self.tol_pos = float(tol_pos)
        self.tol_rot = float(tol_rot)
        self.urdf_path = self._resolve_urdf_path(urdf_path)
        self.model = pin.buildModelFromUrdf(self.urdf_path)
        self.data = self.model.createData()
        self.ee_frame_name = ee_frame_name
        self.ee_frame_id = self._resolve_ee_frame_id(ee_frame_name)
        self._active_q_idx, self._active_v_idx = self._resolve_active_joint_indices()
        if len(self._active_q_idx) != len(self.joint_limits):
            raise RuntimeError("URDF active joint count does not match joint limits")

        self._q_lo = np.array([lo for lo, _ in self.joint_limits], dtype=float)
        self._q_hi = np.array([hi for _, hi in self.joint_limits], dtype=float)
        self.max_joint_vel = np.array([2.2, 2.0, 2.2, 2.2, 2.6, 2.6, 3.0], dtype=float)
        self.min_step_limit = 0.03
        self.jump_detect_scale = 3.0
        self.hard_jump_limit = 0.90
        self.state: ContinuityRuntimeState | None = None
        self.last_report = None
        self.last_jump_report = None
        self.set_tool_offset([0.0] * 6 if tcp_offset is None else tcp_offset)

    def _resolve_urdf_path(self, urdf_path):
        candidates = []
        if urdf_path is not None:
            candidates.append(os.path.abspath(os.path.expanduser(str(urdf_path))))
        env_path = os.getenv("NERO_URDF_PATH")
        if env_path:
            candidates.append(os.path.abspath(os.path.expanduser(env_path)))
        cwd = os.getcwd()
        candidates.extend(
            [
                os.path.join(
                    cwd,
                    "pyAgxArm",
                    "asserts",
                    "agx_arm_urdf",
                    "nero",
                    "urdf",
                    "nero_description.urdf",
                ),
                os.path.join(
                    cwd,
                    "legacy",
                    "nero",
                    "pyAgxArm",
                    "asserts",
                    "agx_arm_urdf",
                    "nero",
                    "urdf",
                    "nero_description.urdf",
                ),
            ]
        )
        for candidate in candidates:
            if os.path.isfile(candidate):
                return candidate
        raise FileNotFoundError("Nero URDF not found. Set NERO_URDF_PATH.")

    def _resolve_ee_frame_id(self, ee_frame_name):
        frame_id = self.model.getFrameId(ee_frame_name)
        if frame_id < self.model.nframes and self.model.frames[frame_id].name == ee_frame_name:
            return frame_id
        raise RuntimeError(f"End-effector frame not found: {ee_frame_name}")

    def _resolve_active_joint_indices(self):
        preferred = [f"joint{i}" for i in range(1, len(self.joint_limits) + 1)]
        all_names = list(self.model.names)
        if all(name in all_names for name in preferred):
            q_idx = []
            v_idx = []
            for name in preferred:
                joint_id = self.model.getJointId(name)
                joint_model = self.model.joints[joint_id]
                q_idx.append(joint_model.idx_q)
                v_idx.append(joint_model.idx_v)
            return q_idx, v_idx

        q_idx = []
        v_idx = []
        for joint_id in range(1, self.model.njoints):
            joint_model = self.model.joints[joint_id]
            if joint_model.nq == 1 and joint_model.nv == 1:
                q_idx.append(joint_model.idx_q)
                v_idx.append(joint_model.idx_v)
        return q_idx[: len(self.joint_limits)], v_idx[: len(self.joint_limits)]

    def set_tool_offset(self, tcp_offset):
        self.tcp_offset = np.asarray(tcp_offset, dtype=float).reshape(-1)
        if self.tcp_offset.size != 6:
            raise ValueError(f"Expected 6 tcp_offset values, got {self.tcp_offset.size}")
        self._T_ee_tcp = pose6_to_matrix(self.tcp_offset)
        self._T_tcp_ee = np.linalg.inv(self._T_ee_tcp)

    def _to_full_q(self, q):
        q_full = pin.neutral(self.model)
        q = np.asarray(q, dtype=float).reshape(-1)
        for i, q_idx in enumerate(self._active_q_idx):
            q_full[q_idx] = q[i]
        return q_full

    def fk_matrix(self, q):
        q_full = self._to_full_q(self._clamp_joints(q))
        pin.forwardKinematics(self.model, self.data, q_full)
        pin.updateFramePlacement(self.model, self.data, self.ee_frame_id)
        placement = self.data.oMf[self.ee_frame_id]
        transform = np.eye(4, dtype=float)
        transform[:3, :3] = np.asarray(placement.rotation, dtype=float)
        transform[:3, 3] = np.asarray(placement.translation, dtype=float)
        return transform @ self._T_ee_tcp

    def fk_pose(self, q):
        transform = self.fk_matrix(q)
        return np.concatenate([transform[:3, 3], matrix_to_rpy(transform[:3, :3])])

    def init_state(self, current_q):
        self.state = ContinuityRuntimeState(q_prev=self._clamp_joints(current_q))

    def solve(self, target_pose, limit_output_step: bool = True):
        target_pose = np.asarray(target_pose, dtype=float).reshape(-1)
        if target_pose.size != 6:
            raise ValueError(f"Expected 6 pose values, got {target_pose.size}")

        if self.state is None or self.state.q_prev is None:
            q = 0.5 * (self._q_lo + self._q_hi)
            self.state = ContinuityRuntimeState(q_prev=q.copy())
        else:
            q = np.asarray(self.state.q_prev, dtype=float).reshape(-1)

        target_tcp = pose6_to_matrix(target_pose)
        target_ee = target_tcp @ self._T_tcp_ee
        target_se3 = pin.SE3(target_ee[:3, :3], target_ee[:3, 3])
        q = self._clamp_joints(q)
        q_full = self._to_full_q(q)
        converged = False
        pos_err = float("inf")
        rot_err = float("inf")
        iterations = 0

        for i in range(self.max_iterations):
            iterations = i + 1
            pin.forwardKinematics(self.model, self.data, q_full)
            pin.updateFramePlacement(self.model, self.data, self.ee_frame_id)
            current_se3 = self.data.oMf[self.ee_frame_id]
            err6 = pin.log6(current_se3.inverse() * target_se3).vector
            pos_err = float(np.linalg.norm(err6[:3]))
            rot_err = float(np.linalg.norm(err6[3:]))
            if pos_err < self.tol_pos and rot_err < self.tol_rot:
                converged = True
                break
            jacobian_full = pin.computeFrameJacobian(
                self.model,
                self.data,
                q_full,
                self.ee_frame_id,
                pin.ReferenceFrame.LOCAL,
            )
            jacobian = jacobian_full[:, self._active_v_idx]
            hessian = jacobian @ jacobian.T + self.damping * np.eye(6)
            dq = jacobian.T @ np.linalg.solve(hessian, err6)
            dq = np.clip(dq, -self._compute_step_limit(), self._compute_step_limit())
            q = self._clamp_joints(q + dq)
            q_full = self._to_full_q(q)

        self.last_report = {
            "method": "pinocchio_dls",
            "converged": bool(converged),
            "iterations": iterations,
            "pos_error_m": pos_err,
            "rot_error_rad": rot_err,
            "urdf_path": self.urdf_path,
            "ee_frame": self.ee_frame_name,
        }
        if not converged:
            return None

        q_clamped = self._clamp_joints(q)
        q_out, jump_report = (
            self._detect_and_guard_output(q_clamped)
            if limit_output_step
            else (q_clamped, {"jump_detected": False, "mode": "bypass_rate_limit"})
        )
        self.last_jump_report = jump_report
        previous = self.state.q_prev.copy() if self.state and self.state.q_prev is not None else q_out.copy()
        self.state = ContinuityRuntimeState(q_prev=q_out, q_prev2=previous, q_lock=q_out)
        return q_out

    def _clamp_joints(self, q):
        q_out = np.asarray(q, dtype=float).reshape(-1).copy()
        for i, (lo, hi) in enumerate(self.joint_limits):
            q_out[i] = min(max(q_out[i], lo), hi)
        return q_out

    def _compute_step_limit(self):
        return np.maximum(self.max_joint_vel * self.dt, self.min_step_limit)

    def _detect_and_guard_output(self, q_cmd):
        if self.state is None or self.state.q_prev is None:
            return self._clamp_joints(q_cmd), {"jump_detected": False, "mode": "no_prev_state"}
        q_prev = np.asarray(self.state.q_prev, dtype=float)
        dq_raw = (np.asarray(q_cmd, dtype=float) - q_prev + np.pi) % (2.0 * np.pi) - np.pi
        step_limit = self._compute_step_limit()
        detect_limit = np.maximum(step_limit * self.jump_detect_scale, self.min_step_limit)
        jump_mask = np.abs(dq_raw) > detect_limit
        very_large_jump = bool(np.any(np.abs(dq_raw) > self.hard_jump_limit))
        dq_limited = np.clip(dq_raw, -step_limit, step_limit)
        q_safe = q_prev.copy() if very_large_jump else self._clamp_joints(q_prev + dq_limited)
        return q_safe, {
            "jump_detected": bool(np.any(jump_mask)),
            "joint_indices": np.where(jump_mask)[0].astype(int).tolist(),
            "very_large_jump": very_large_jump,
            "mode": "freeze" if very_large_jump else "rate_limit",
        }


Pinocchio_Solver = PinocchioSolver

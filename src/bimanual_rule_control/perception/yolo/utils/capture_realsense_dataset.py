#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Capture RGB-D dataset from Intel RealSense D405 / D435i.

Features:
    1. Save RGB images.
    2. Save aligned depth images as 16-bit PNG.
    3. Save camera intrinsics to intrinsics.json.
    4. Save capture metadata to metadata.csv.
    5. Support keyboard manual save / pause / quit.

Keyboard:
    s       manual save current frame
    p       pause / resume automatic capture
    q / ESC quit

Dependencies:
    pip install pyrealsense2 opencv-python numpy
"""

import csv
import json
import time
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np
import pyrealsense2 as rs


# ============================================================
# User Config
# ============================================================

CONFIG = {
    # ---------------- Camera Selection ----------------
    # 可选: "D405" 或 "D435i"
    "camera_model": "D435i",

    # D405: 412622270929 | 412622270701
    # D435i: 339322074423
    "serial_number": "317422075656",

    # ---------------- Capture Schedule ----------------
    # 每 i 秒拍摄 j 张
    "interval_seconds": 1.0,   # i
    "shots_per_round": 5,      # j

    # 每轮拍摄完成后暂停 k 秒
    "pause_seconds": 5.0,      # k

    # 总共拍摄 n 张后退出
    "total_images": 10,       # n

    # ---------------- Image Settings ----------------
    # RGB 图片格式，支持: "jpg", "jpeg", "png"
    "image_format": "jpg",

    # RGB / Depth 对齐到 color 坐标系
    # 常用: 640x480, 848x480, 1280x720
    "width": 424,
    "height": 240,
    "fps": 30,

    # ---------------- Output Settings ----------------
    "output_dir": "./datasets/realsense_rgbd_capture",

    # 文件命名格式:
    # <filename_prefix>_<拍摄序号>.<image_format>
    # 例如: d405_black_cap_000001.jpg
    "filename_prefix": "d405_black_cap_tube",

    # 拍摄序号从几开始
    "start_index": 1,

    # 序号位数
    "index_digits": 4,

    # ---------------- Runtime Settings ----------------
    # 是否保存前先预热相机若干帧
    "warmup_frames": 30,

    # 是否显示实时画面
    "show_preview": True,

    # 是否在 preview 中叠加 depth 可视化
    "show_depth_preview": True,

    # 自动采集模式下，如果暂停，是否仍然允许 s 手动保存
    "allow_manual_save_when_paused": True,
}


# ============================================================
# Config / IO Helpers
# ============================================================

def validate_config(cfg: dict) -> None:
    image_format = cfg["image_format"].lower()
    if image_format == "jpeg":
        image_format = "jpg"
    cfg["image_format"] = image_format

    if image_format not in {"jpg", "png"}:
        raise ValueError(
            f"Unsupported image_format: {cfg['image_format']}. "
            "Use 'jpg', 'jpeg', or 'png'."
        )

    if cfg["camera_model"] not in {"D405", "D435i"}:
        raise ValueError("camera_model must be 'D405' or 'D435i'.")

    if cfg["interval_seconds"] <= 0:
        raise ValueError("interval_seconds must be > 0.")

    if cfg["shots_per_round"] <= 0:
        raise ValueError("shots_per_round must be > 0.")

    if cfg["pause_seconds"] < 0:
        raise ValueError("pause_seconds must be >= 0.")

    if cfg["total_images"] <= 0:
        raise ValueError("total_images must be > 0.")

    if cfg["width"] <= 0 or cfg["height"] <= 0:
        raise ValueError("width and height must be > 0.")

    if cfg["fps"] <= 0:
        raise ValueError("fps must be > 0.")


def make_output_dirs(output_dir: str) -> dict:
    root = Path(output_dir).expanduser().resolve()

    dirs = {
        "root": root,
        "color": root / "color",
        "depth": root / "depth",
        "meta": root / "meta",
    }

    for p in dirs.values():
        p.mkdir(parents=True, exist_ok=True)

    return dirs


def build_stem(cfg: dict, index: int) -> str:
    prefix = cfg["filename_prefix"]
    digits = int(cfg["index_digits"])
    return f"{prefix}_{index:0{digits}d}"


def save_color_image(image_bgr: np.ndarray, save_path: Path, image_format: str) -> None:
    if image_format == "jpg":
        ok = cv2.imwrite(str(save_path), image_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    elif image_format == "png":
        ok = cv2.imwrite(str(save_path), image_bgr, [cv2.IMWRITE_PNG_COMPRESSION, 3])
    else:
        raise ValueError(f"Unsupported image_format: {image_format}")

    if not ok:
        raise RuntimeError(f"Failed to save color image: {save_path}")


def save_depth_image(depth_raw: np.ndarray, save_path: Path) -> None:
    """
    Save depth image as 16-bit PNG.

    depth_raw should usually be uint16 from RealSense.
    Unit is raw depth unit. Convert to meters by:
        depth_m = depth_raw * depth_scale
    """
    if depth_raw.dtype != np.uint16:
        depth_raw = depth_raw.astype(np.uint16)

    ok = cv2.imwrite(str(save_path), depth_raw)
    if not ok:
        raise RuntimeError(f"Failed to save depth image: {save_path}")


def write_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================
# RealSense Helpers
# ============================================================

def create_realsense_pipeline(cfg: dict):
    pipeline = rs.pipeline()
    rs_config = rs.config()

    serial_number = str(cfg["serial_number"])
    rs_config.enable_device(serial_number)

    # Color stream
    rs_config.enable_stream(
        rs.stream.color,
        int(cfg["width"]),
        int(cfg["height"]),
        rs.format.bgr8,
        int(cfg["fps"]),
    )

    # Depth stream
    rs_config.enable_stream(
        rs.stream.depth,
        int(cfg["width"]),
        int(cfg["height"]),
        rs.format.z16,
        int(cfg["fps"]),
    )

    print("[INFO] Starting RealSense pipeline...")
    print(f"[INFO] Camera model: {cfg['camera_model']}")
    print(f"[INFO] Serial number: {serial_number}")
    print(f"[INFO] Resolution: {cfg['width']}x{cfg['height']} @ {cfg['fps']} FPS")

    profile = pipeline.start(rs_config)

    device = profile.get_device()
    device_name = device.get_info(rs.camera_info.name)
    device_serial = device.get_info(rs.camera_info.serial_number)

    print(f"[INFO] Connected device: {device_name}")
    print(f"[INFO] Connected serial: {device_serial}")

    if device_serial != serial_number:
        raise RuntimeError(
            f"Connected serial mismatch. Expected {serial_number}, got {device_serial}"
        )

    depth_sensor = device.first_depth_sensor()
    depth_scale = float(depth_sensor.get_depth_scale())
    print(f"[INFO] Depth scale: {depth_scale} meter / raw unit")

    align_to_color = rs.align(rs.stream.color)

    return pipeline, profile, align_to_color, depth_scale, device_name, device_serial


def warmup_camera(pipeline, align_to_color, warmup_frames: int) -> None:
    if warmup_frames <= 0:
        return

    print(f"[INFO] Warming up camera for {warmup_frames} frames...")
    for _ in range(warmup_frames):
        frames = pipeline.wait_for_frames()
        _ = align_to_color.process(frames)

    print("[INFO] Warmup complete.")


def get_aligned_rgbd_frame(pipeline, align_to_color):
    """
    Return:
        color_bgr: H x W x 3, uint8, BGR
        depth_raw: H x W, uint16, aligned to color frame
        color_frame
        depth_frame
    """
    frames = pipeline.wait_for_frames()
    aligned_frames = align_to_color.process(frames)

    color_frame = aligned_frames.get_color_frame()
    depth_frame = aligned_frames.get_depth_frame()

    if not color_frame:
        raise RuntimeError("Failed to get color frame.")

    if not depth_frame:
        raise RuntimeError("Failed to get depth frame.")

    color_bgr = np.asanyarray(color_frame.get_data())
    depth_raw = np.asanyarray(depth_frame.get_data())

    return color_bgr, depth_raw, color_frame, depth_frame


def intrinsics_to_dict(intr: rs.intrinsics) -> dict:
    return {
        "width": int(intr.width),
        "height": int(intr.height),
        "fx": float(intr.fx),
        "fy": float(intr.fy),
        "ppx": float(intr.ppx),
        "ppy": float(intr.ppy),
        "cx": float(intr.ppx),
        "cy": float(intr.ppy),
        "model": str(intr.model),
        "coeffs": [float(x) for x in intr.coeffs],
    }


def save_intrinsics_json(
    path: Path,
    cfg: dict,
    profile,
    depth_scale: float,
    device_name: str,
    device_serial: str,
) -> None:
    color_stream = profile.get_stream(rs.stream.color).as_video_stream_profile()
    depth_stream = profile.get_stream(rs.stream.depth).as_video_stream_profile()

    color_intr = color_stream.get_intrinsics()
    depth_intr = depth_stream.get_intrinsics()

    data = {
        "camera_model_config": cfg["camera_model"],
        "device_name": device_name,
        "serial_number": device_serial,
        "width": int(cfg["width"]),
        "height": int(cfg["height"]),
        "fps": int(cfg["fps"]),
        "depth_scale": depth_scale,
        "note": (
            "Depth images are saved as uint16 PNG. "
            "Aligned depth frames are aligned to color stream. "
            "Use color_intrinsics for RGB pixel deprojection when using aligned depth."
        ),
        "color_intrinsics": intrinsics_to_dict(color_intr),
        "depth_intrinsics_original": intrinsics_to_dict(depth_intr),
    }

    write_json(path, data)
    print(f"[INFO] Saved intrinsics: {path}")


# ============================================================
# Metadata CSV
# ============================================================

def create_metadata_writer(csv_path: Path):
    f = csv_path.open("w", newline="", encoding="utf-8")

    fieldnames = [
        "index",
        "timestamp_iso",
        "timestamp_unix",
        "camera_model_config",
        "device_name",
        "serial_number",
        "width",
        "height",
        "fps",
        "color_path",
        "depth_path",
        "image_format",
        "depth_format",
        "depth_scale",
        "capture_mode",
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    return f, writer


def write_metadata_row(
    writer,
    *,
    index: int,
    cfg: dict,
    device_name: str,
    device_serial: str,
    color_path: Path,
    depth_path: Path,
    depth_scale: float,
    capture_mode: str,
) -> None:
    now = datetime.now()

    writer.writerow({
        "index": index,
        "timestamp_iso": now.isoformat(timespec="milliseconds"),
        "timestamp_unix": f"{time.time():.6f}",
        "camera_model_config": cfg["camera_model"],
        "device_name": device_name,
        "serial_number": device_serial,
        "width": int(cfg["width"]),
        "height": int(cfg["height"]),
        "fps": int(cfg["fps"]),
        "color_path": str(color_path),
        "depth_path": str(depth_path),
        "image_format": cfg["image_format"],
        "depth_format": "png_uint16",
        "depth_scale": depth_scale,
        "capture_mode": capture_mode,
    })


# ============================================================
# Preview / Keyboard
# ============================================================

def make_preview(color_bgr: np.ndarray, depth_raw: np.ndarray, status_text: str, show_depth: bool):
    color_vis = color_bgr.copy()

    cv2.putText(
        color_vis,
        status_text,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        color_vis,
        "keys: s=save, p=pause/resume, q/ESC=quit",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 255),
        1,
        cv2.LINE_AA,
    )

    if not show_depth:
        return color_vis

    depth_vis = cv2.convertScaleAbs(depth_raw, alpha=0.03)
    depth_vis = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)

    if depth_vis.shape[:2] != color_vis.shape[:2]:
        depth_vis = cv2.resize(depth_vis, (color_vis.shape[1], color_vis.shape[0]))

    combined = np.hstack([color_vis, depth_vis])
    return combined


def handle_key(key: int, paused: bool):
    """
    Return:
        action: "none" | "save" | "quit"
        paused: updated pause state
    """
    if key < 0:
        return "none", paused

    key = key & 0xFF

    if key in {27, ord("q")}:
        return "quit", paused

    if key == ord("p"):
        paused = not paused
        print(f"[KEY] {'Paused' if paused else 'Resumed'} automatic capture.")
        return "none", paused

    if key == ord("s"):
        print("[KEY] Manual save requested.")
        return "save", paused

    return "none", paused


# ============================================================
# Save Current Frame
# ============================================================

def save_current_rgbd(
    *,
    cfg: dict,
    dirs: dict,
    index: int,
    color_bgr: np.ndarray,
    depth_raw: np.ndarray,
    metadata_writer,
    metadata_file,
    device_name: str,
    device_serial: str,
    depth_scale: float,
    capture_mode: str,
) -> tuple[int, Path, Path]:
    stem = build_stem(cfg, index)

    color_path = dirs["color"] / f"{stem}.{cfg['image_format']}"
    depth_path = dirs["depth"] / f"{stem}_depth.png"

    save_color_image(color_bgr, color_path, cfg["image_format"])
    save_depth_image(depth_raw, depth_path)

    write_metadata_row(
        metadata_writer,
        index=index,
        cfg=cfg,
        device_name=device_name,
        device_serial=device_serial,
        color_path=color_path,
        depth_path=depth_path,
        depth_scale=depth_scale,
        capture_mode=capture_mode,
    )
    metadata_file.flush()

    return index + 1, color_path, depth_path


# ============================================================
# Main Capture Logic
# ============================================================

def main():
    cfg = CONFIG.copy()
    validate_config(cfg)

    dirs = make_output_dirs(cfg["output_dir"])

    print("============================================================")
    print("[INFO] RealSense RGB-D Dataset Capture")
    print("============================================================")
    print(f"[INFO] Output root: {dirs['root']}")
    print(f"[INFO] Color dir:   {dirs['color']}")
    print(f"[INFO] Depth dir:   {dirs['depth']}")
    print(f"[INFO] Meta dir:    {dirs['meta']}")
    print(f"[INFO] Filename format: {cfg['filename_prefix']}_<index>.{cfg['image_format']}")
    print(f"[INFO] Capture rule: every {cfg['interval_seconds']} s capture "
          f"{cfg['shots_per_round']} images, then pause {cfg['pause_seconds']} s")
    print(f"[INFO] Total target images: {cfg['total_images']}")
    print("[INFO] Keyboard: s=manual save, p=pause/resume, q/ESC=quit")
    print("============================================================")

    pipeline = None
    metadata_file = None

    captured_count = 0
    current_index = int(cfg["start_index"])
    paused = False

    try:
        pipeline, profile, align_to_color, depth_scale, device_name, device_serial = (
            create_realsense_pipeline(cfg)
        )

        warmup_camera(pipeline, align_to_color, int(cfg["warmup_frames"]))

        intrinsics_path = dirs["meta"] / "intrinsics.json"
        save_intrinsics_json(
            intrinsics_path,
            cfg,
            profile,
            depth_scale,
            device_name,
            device_serial,
        )

        metadata_path = dirs["meta"] / "metadata.csv"
        metadata_file, metadata_writer = create_metadata_writer(metadata_path)
        print(f"[INFO] Metadata CSV: {metadata_path}")

        while captured_count < cfg["total_images"]:
            remaining = cfg["total_images"] - captured_count
            shots_this_round = min(int(cfg["shots_per_round"]), remaining)

            print("")
            print(f"[INFO] Starting new round: target {shots_this_round} automatic image(s).")
            print(f"[INFO] Progress: {captured_count}/{cfg['total_images']}")

            round_auto_saved = 0

            while round_auto_saved < shots_this_round and captured_count < cfg["total_images"]:
                shot_start_time = time.time()

                # Wait until not paused, while still previewing and allowing manual save / quit.
                while True:
                    color_bgr, depth_raw, _, _ = get_aligned_rgbd_frame(pipeline, align_to_color)

                    status = (
                        f"{captured_count}/{cfg['total_images']} saved | "
                        f"{'PAUSED' if paused else 'AUTO'} | "
                        f"round {round_auto_saved}/{shots_this_round}"
                    )

                    if cfg["show_preview"]:
                        preview = make_preview(
                            color_bgr,
                            depth_raw,
                            status,
                            bool(cfg["show_depth_preview"]),
                        )
                        cv2.imshow("RealSense RGB-D Capture", preview)
                        key = cv2.waitKey(1)
                    else:
                        key = -1

                    action, paused = handle_key(key, paused)

                    if action == "quit":
                        print("[INFO] Quit requested.")
                        return

                    if action == "save" and (
                        cfg["allow_manual_save_when_paused"] or not paused
                    ):
                        current_index, color_path, depth_path = save_current_rgbd(
                            cfg=cfg,
                            dirs=dirs,
                            index=current_index,
                            color_bgr=color_bgr,
                            depth_raw=depth_raw,
                            metadata_writer=metadata_writer,
                            metadata_file=metadata_file,
                            device_name=device_name,
                            device_serial=device_serial,
                            depth_scale=depth_scale,
                            capture_mode="manual",
                        )

                        captured_count += 1

                        print(
                            f"[MANUAL SAVE] {captured_count}/{cfg['total_images']} "
                            f"color={color_path.name}, depth={depth_path.name}"
                        )

                        if captured_count >= cfg["total_images"]:
                            break

                    if not paused:
                        break

                    time.sleep(0.01)

                if captured_count >= cfg["total_images"]:
                    break

                # Automatic save current frame.
                color_bgr, depth_raw, _, _ = get_aligned_rgbd_frame(pipeline, align_to_color)

                current_index, color_path, depth_path = save_current_rgbd(
                    cfg=cfg,
                    dirs=dirs,
                    index=current_index,
                    color_bgr=color_bgr,
                    depth_raw=depth_raw,
                    metadata_writer=metadata_writer,
                    metadata_file=metadata_file,
                    device_name=device_name,
                    device_serial=device_serial,
                    depth_scale=depth_scale,
                    capture_mode="auto",
                )

                captured_count += 1
                round_auto_saved += 1

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[AUTO SAVE] {captured_count}/{cfg['total_images']} "
                    f"color={color_path.name}, depth={depth_path.name} | {timestamp}"
                )

                # Show updated preview and handle one key.
                if cfg["show_preview"]:
                    status = (
                        f"{captured_count}/{cfg['total_images']} saved | AUTO | "
                        f"round {round_auto_saved}/{shots_this_round}"
                    )
                    preview = make_preview(
                        color_bgr,
                        depth_raw,
                        status,
                        bool(cfg["show_depth_preview"]),
                    )
                    cv2.imshow("RealSense RGB-D Capture", preview)
                    key = cv2.waitKey(1)
                    action, paused = handle_key(key, paused)

                    if action == "quit":
                        print("[INFO] Quit requested.")
                        return

                    if action == "save":
                        # Avoid double-saving exactly at the same instant only if the user pressed s.
                        if captured_count < cfg["total_images"]:
                            current_index, color_path, depth_path = save_current_rgbd(
                                cfg=cfg,
                                dirs=dirs,
                                index=current_index,
                                color_bgr=color_bgr,
                                depth_raw=depth_raw,
                                metadata_writer=metadata_writer,
                                metadata_file=metadata_file,
                                device_name=device_name,
                                device_serial=device_serial,
                                depth_scale=depth_scale,
                                capture_mode="manual",
                            )
                            captured_count += 1
                            print(
                                f"[MANUAL SAVE] {captured_count}/{cfg['total_images']} "
                                f"color={color_path.name}, depth={depth_path.name}"
                            )

                if captured_count >= cfg["total_images"]:
                    break

                elapsed = time.time() - shot_start_time
                wait_time = max(0.0, float(cfg["interval_seconds"]) - elapsed)

                # Wait between automatic shots while keeping keyboard responsive.
                wait_until = time.time() + wait_time
                while time.time() < wait_until and captured_count < cfg["total_images"]:
                    color_bgr, depth_raw, _, _ = get_aligned_rgbd_frame(pipeline, align_to_color)

                    status = (
                        f"{captured_count}/{cfg['total_images']} saved | "
                        f"{'PAUSED' if paused else 'WAIT'} | "
                        f"next auto in {max(0.0, wait_until - time.time()):.1f}s"
                    )

                    if cfg["show_preview"]:
                        preview = make_preview(
                            color_bgr,
                            depth_raw,
                            status,
                            bool(cfg["show_depth_preview"]),
                        )
                        cv2.imshow("RealSense RGB-D Capture", preview)
                        key = cv2.waitKey(1)
                    else:
                        key = -1

                    action, paused = handle_key(key, paused)

                    if action == "quit":
                        print("[INFO] Quit requested.")
                        return

                    if action == "save" and (
                        cfg["allow_manual_save_when_paused"] or not paused
                    ):
                        current_index, color_path, depth_path = save_current_rgbd(
                            cfg=cfg,
                            dirs=dirs,
                            index=current_index,
                            color_bgr=color_bgr,
                            depth_raw=depth_raw,
                            metadata_writer=metadata_writer,
                            metadata_file=metadata_file,
                            device_name=device_name,
                            device_serial=device_serial,
                            depth_scale=depth_scale,
                            capture_mode="manual",
                        )
                        captured_count += 1
                        print(
                            f"[MANUAL SAVE] {captured_count}/{cfg['total_images']} "
                            f"color={color_path.name}, depth={depth_path.name}"
                        )

                    # If paused during between-shot wait, stay here until resumed.
                    while paused and captured_count < cfg["total_images"]:
                        color_bgr, depth_raw, _, _ = get_aligned_rgbd_frame(pipeline, align_to_color)

                        status = (
                            f"{captured_count}/{cfg['total_images']} saved | PAUSED | "
                            f"s=manual save, p=resume"
                        )

                        if cfg["show_preview"]:
                            preview = make_preview(
                                color_bgr,
                                depth_raw,
                                status,
                                bool(cfg["show_depth_preview"]),
                            )
                            cv2.imshow("RealSense RGB-D Capture", preview)
                            key = cv2.waitKey(1)
                        else:
                            key = -1

                        action, paused = handle_key(key, paused)

                        if action == "quit":
                            print("[INFO] Quit requested.")
                            return

                        if action == "save" and cfg["allow_manual_save_when_paused"]:
                            current_index, color_path, depth_path = save_current_rgbd(
                                cfg=cfg,
                                dirs=dirs,
                                index=current_index,
                                color_bgr=color_bgr,
                                depth_raw=depth_raw,
                                metadata_writer=metadata_writer,
                                metadata_file=metadata_file,
                                device_name=device_name,
                                device_serial=device_serial,
                                depth_scale=depth_scale,
                                capture_mode="manual",
                            )
                            captured_count += 1
                            print(
                                f"[MANUAL SAVE] {captured_count}/{cfg['total_images']} "
                                f"color={color_path.name}, depth={depth_path.name}"
                            )

                        time.sleep(0.01)

                    time.sleep(0.01)

            if captured_count >= cfg["total_images"]:
                break

            # Round pause with responsive keyboard.
            print("")
            print("------------------------------------------------------------")
            print(
                f"[PAUSE] Round finished. Captured {captured_count}/"
                f"{cfg['total_images']} images."
            )
            print(f"[PAUSE] Waiting {cfg['pause_seconds']} seconds before next round...")
            print("[PAUSE] Press s to manually save, p to pause/resume, q/ESC to quit.")
            print("------------------------------------------------------------")

            pause_until = time.time() + float(cfg["pause_seconds"])

            while time.time() < pause_until and captured_count < cfg["total_images"]:
                color_bgr, depth_raw, _, _ = get_aligned_rgbd_frame(pipeline, align_to_color)

                status = (
                    f"{captured_count}/{cfg['total_images']} saved | ROUND PAUSE | "
                    f"next round in {max(0.0, pause_until - time.time()):.1f}s"
                )

                if cfg["show_preview"]:
                    preview = make_preview(
                        color_bgr,
                        depth_raw,
                        status,
                        bool(cfg["show_depth_preview"]),
                    )
                    cv2.imshow("RealSense RGB-D Capture", preview)
                    key = cv2.waitKey(1)
                else:
                    key = -1

                action, paused = handle_key(key, paused)

                if action == "quit":
                    print("[INFO] Quit requested.")
                    return

                if action == "save" and (
                    cfg["allow_manual_save_when_paused"] or not paused
                ):
                    current_index, color_path, depth_path = save_current_rgbd(
                        cfg=cfg,
                        dirs=dirs,
                        index=current_index,
                        color_bgr=color_bgr,
                        depth_raw=depth_raw,
                        metadata_writer=metadata_writer,
                        metadata_file=metadata_file,
                        device_name=device_name,
                        device_serial=device_serial,
                        depth_scale=depth_scale,
                        capture_mode="manual",
                    )
                    captured_count += 1
                    print(
                        f"[MANUAL SAVE] {captured_count}/{cfg['total_images']} "
                        f"color={color_path.name}, depth={depth_path.name}"
                    )

                while paused and captured_count < cfg["total_images"]:
                    color_bgr, depth_raw, _, _ = get_aligned_rgbd_frame(pipeline, align_to_color)

                    status = (
                        f"{captured_count}/{cfg['total_images']} saved | PAUSED | "
                        f"s=manual save, p=resume"
                    )

                    if cfg["show_preview"]:
                        preview = make_preview(
                            color_bgr,
                            depth_raw,
                            status,
                            bool(cfg["show_depth_preview"]),
                        )
                        cv2.imshow("RealSense RGB-D Capture", preview)
                        key = cv2.waitKey(1)
                    else:
                        key = -1

                    action, paused = handle_key(key, paused)

                    if action == "quit":
                        print("[INFO] Quit requested.")
                        return

                    if action == "save" and cfg["allow_manual_save_when_paused"]:
                        current_index, color_path, depth_path = save_current_rgbd(
                            cfg=cfg,
                            dirs=dirs,
                            index=current_index,
                            color_bgr=color_bgr,
                            depth_raw=depth_raw,
                            metadata_writer=metadata_writer,
                            metadata_file=metadata_file,
                            device_name=device_name,
                            device_serial=device_serial,
                            depth_scale=depth_scale,
                            capture_mode="manual",
                        )
                        captured_count += 1
                        print(
                            f"[MANUAL SAVE] {captured_count}/{cfg['total_images']} "
                            f"color={color_path.name}, depth={depth_path.name}"
                        )

                    time.sleep(0.01)

                time.sleep(0.01)

        print("")
        print("============================================================")
        print(f"[DONE] Capture complete. Total saved image pairs: {captured_count}")
        print(f"[DONE] Output root: {dirs['root']}")
        print(f"[DONE] Color images: {dirs['color']}")
        print(f"[DONE] Depth images: {dirs['depth']}")
        print(f"[DONE] Intrinsics: {dirs['meta'] / 'intrinsics.json'}")
        print(f"[DONE] Metadata: {dirs['meta'] / 'metadata.csv'}")
        print("============================================================")

    except KeyboardInterrupt:
        print("")
        print("[INFO] KeyboardInterrupt received. Exiting safely.")

    finally:
        if metadata_file is not None:
            metadata_file.close()
            print("[INFO] Metadata CSV closed.")

        if pipeline is not None:
            pipeline.stop()
            print("[INFO] RealSense pipeline stopped.")

        if cfg["show_preview"]:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
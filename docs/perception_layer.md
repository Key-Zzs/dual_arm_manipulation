# Perception Layer

The perception layer owns cameras, image processing, detection, pose estimates,
and calibration utilities.

Current interfaces and placeholders:

- `CameraManager`
- `RealSenseCamera`
- `MockCamera`
- `OpenCVTubeCapDetector`
- `OpenCVRackDetector`
- `OpenCVHoleDetector`
- `YOLODetector`
- `YOLOSegmentor`
- `AprilTagDetector`
- `transform_from_config`

The placeholder detectors currently return no detections unless configured in
mock mode. Task dry-run uses mock observations in the task state handlers, so it
does not require real cameras or detector models.

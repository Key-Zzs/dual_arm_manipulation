import cv2
import numpy as np
import argparse


def make_depth_colormap(depth_raw):
    valid = depth_raw[depth_raw > 0]

    if len(valid) == 0:
        return np.zeros((*depth_raw.shape, 3), dtype=np.uint8)

    vmin = np.percentile(valid, 2)
    vmax = np.percentile(valid, 98)

    if vmax <= vmin:
        vmax = vmin + 1

    depth_norm = np.clip(
        (depth_raw.astype(np.float32) - vmin) / (vmax - vmin),
        0,
        1,
    )

    depth_vis = (depth_norm * 255).astype(np.uint8)
    depth_color = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)
    depth_color[depth_raw == 0] = (0, 0, 0)

    return depth_color


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("depth_path", type=str)
    parser.add_argument("--save", type=str, default=None)
    args = parser.parse_args()

    depth = cv2.imread(args.depth_path, cv2.IMREAD_UNCHANGED)

    if depth is None:
        raise FileNotFoundError(args.depth_path)

    print("dtype:", depth.dtype)
    print("shape:", depth.shape)
    print("min:", depth.min())
    print("max:", depth.max())
    print("nonzero ratio:", np.count_nonzero(depth) / depth.size)

    valid = depth[depth > 0]
    if len(valid) > 0:
        print("valid min:", valid.min())
        print("valid max:", valid.max())
        print("valid median:", np.median(valid))

    depth_color = make_depth_colormap(depth)

    if args.save:
        cv2.imwrite(args.save, depth_color)
        print("saved:", args.save)

    cv2.imshow("depth color", depth_color)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
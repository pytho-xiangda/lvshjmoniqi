"""Build a 12-frame, color-matched walk atlas from four approved key poses."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CHARACTER_DIR = ROOT / "assets" / "art" / "daily" / "characters"
WORK_DIR = ROOT / ".audio_runtime" / "daily-room-smooth"
FRAME_WIDTH = 384
FRAME_HEIGHT = 530
FRAME_COUNT = 12


def color_match(image: Image.Image) -> Image.Image:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.float32)
    rgb = rgba[..., :3]
    alpha = rgba[..., 3:4]
    luminance = rgb[..., 0:1] * 0.299 + rgb[..., 1:2] * 0.587 + rgb[..., 2:3] * 0.114
    rgb = luminance + (rgb - luminance) * 0.84
    rgb = (rgb - 128.0) * 0.94 + 128.0
    rgb = rgb * 0.95 + np.array([126.0, 91.0, 62.0], dtype=np.float32) * 0.05
    rgba[..., :3] = np.clip(rgb, 0, 255)
    rgba[..., 3:4] = alpha
    return Image.fromarray(rgba.astype(np.uint8), "RGBA")


def composite_on_key(image: Image.Image) -> Image.Image:
    backing = Image.new("RGBA", image.size, (255, 0, 255, 255))
    backing.alpha_composite(image)
    return backing.convert("RGB")


def remove_key(image: Image.Image) -> Image.Image:
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    magenta_score = np.minimum(rgb[..., 0] - rgb[..., 1], rgb[..., 2] - rgb[..., 1])
    alpha = np.clip(1.0 - (magenta_score - 3.0) / 72.0, 0.0, 1.0)
    alpha[magenta_score <= 3.0] = 1.0

    # Motion interpolation mixes the matte into antialiased edge pixels. Fill
    # those edge colors from nearby solid character pixels before applying alpha.
    filled = rgb.copy()
    valid = (alpha > 0.98) & (magenta_score <= 3.0)
    needs_color = (alpha > 0.02) & ~valid
    height, width = alpha.shape
    for _ in range(28):
        total = np.zeros_like(filled)
        count = np.zeros((height, width, 1), dtype=np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            shifted_color = np.roll(filled, (dy, dx), axis=(0, 1))
            shifted_valid = np.roll(valid, (dy, dx), axis=(0, 1))
            if dy < 0:
                shifted_valid[dy:] = False
            elif dy > 0:
                shifted_valid[:dy] = False
            if dx < 0:
                shifted_valid[:, dx:] = False
            elif dx > 0:
                shifted_valid[:, :dx] = False
            total += shifted_color * shifted_valid[..., None]
            count += shifted_valid[..., None]
        newly_filled = needs_color & ~valid & (count[..., 0] > 0)
        if not newly_filled.any():
            break
        filled[newly_filled] = (total / np.maximum(count, 1.0))[newly_filled]
        valid[newly_filled] = True
    alpha[needs_color & ~valid] = 0.0
    rgba = np.concatenate([np.clip(filled, 0, 255), alpha[..., None] * 255.0], axis=2)
    rgba[alpha < 0.035] = 0
    return Image.fromarray(rgba.astype(np.uint8), "RGBA")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    source_atlas = Image.open(CHARACTER_DIR / "protagonist_side_walk_v03.png").convert("RGBA")
    key_frames = [
        color_match(source_atlas.crop((index * FRAME_WIDTH, 0, (index + 1) * FRAME_WIDTH, FRAME_HEIGHT)))
        for index in range(4)
    ]
    for old_frame in WORK_DIR.glob("key_*.png"):
        old_frame.unlink()
    for old_frame in WORK_DIR.glob("tween_*.png"):
        old_frame.unlink()
    padded_cycle = [key_frames[-1], *key_frames, key_frames[0], key_frames[1]]
    for index, frame in enumerate(padded_cycle):
        composite_on_key(frame).save(WORK_DIR / f"key_{index:02d}.png")

    subprocess.run(
        [
            args.ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-framerate",
            "4",
            "-i",
            str(WORK_DIR / "key_%02d.png"),
            "-vf",
            "minterpolate=fps=12:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,format=rgb24",
            str(WORK_DIR / "tween_%02d.png"),
        ],
        check=True,
    )

    tween_paths = sorted(WORK_DIR.glob("tween_*.png"))
    if len(tween_paths) < FRAME_COUNT:
        raise RuntimeError(f"interpolator returned {len(tween_paths)} frames; need {FRAME_COUNT}")
    start = (len(tween_paths) - FRAME_COUNT) // 2
    frames = [remove_key(Image.open(frame)) for frame in tween_paths[start : start + FRAME_COUNT]]
    atlas = Image.new("RGBA", (FRAME_WIDTH * 6, FRAME_HEIGHT * 2))
    for index, frame in enumerate(frames):
        atlas.alpha_composite(frame, ((index % 6) * FRAME_WIDTH, (index // 6) * FRAME_HEIGHT))
    atlas.save(CHARACTER_DIR / "protagonist_side_walk_v04.png")

    idle = color_match(Image.open(CHARACTER_DIR / "protagonist_side_idle_v03.png"))
    idle.save(CHARACTER_DIR / "protagonist_side_idle_v04.png")
    metadata = {
        "view": "fixed_side",
        "columns": 6,
        "rows": 2,
        "frame_width": FRAME_WIDTH,
        "frame_height": FRAME_HEIGHT,
        "frame_count": FRAME_COUNT,
        "fps": 12,
        "character_height": 470,
        "foot_anchor": [192, 510],
        "room_ground_y": 795,
        "direction": "left",
        "right_direction": "horizontal flip",
        "interpolation": "FFmpeg bidirectional motion-compensated interpolation from four painted key poses",
        "color_match": "reduced saturation and contrast with a restrained walnut ambient tint",
        "frames": [
            {
                "index": index,
                "region": [(index % 6) * FRAME_WIDTH, (index // 6) * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT],
            }
            for index in range(FRAME_COUNT)
        ],
    }
    (CHARACTER_DIR / "protagonist_side_walk_v04.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"frames": FRAME_COUNT, "fps": 12, "atlas": list(atlas.size), "idle": list(idle.size)}))


if __name__ == "__main__":
    main()

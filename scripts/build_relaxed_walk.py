"""Build the taller, relaxed daily-life walk atlas used by the Godot demo."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

from build_natural_walk import keep_largest_component, remove_magenta
from build_smooth_side_sprites import color_match


ROOT = Path(__file__).resolve().parents[1]
CHARACTER_DIR = ROOT / "assets" / "art" / "daily" / "characters"
SOURCE = CHARACTER_DIR / "source_v07" / "relaxed_walk_cycle_sheet.png"
FRAME_WIDTH = 448
FRAME_HEIGHT = 640
FRAME_COUNT = 8
FOOT_Y = 610
CHARACTER_HEIGHT = 540
FPS = 8
WALK_SPEED = 140


def find_sprite_columns(source: Image.Image) -> list[tuple[int, int]]:
    alpha = np.asarray(source.getchannel("A"))
    active_columns = (alpha > 20).sum(axis=0) > 30
    runs: list[tuple[int, int]] = []
    run_start: int | None = None
    for x, active in enumerate(active_columns):
        if active and run_start is None:
            run_start = x
        if run_start is not None and (not active or x == source.width - 1):
            run_end = x if not active else x + 1
            if run_end - run_start > 30:
                runs.append((run_start, run_end))
            run_start = None
    if len(runs) != FRAME_COUNT:
        raise RuntimeError(f"expected {FRAME_COUNT} character columns, found {len(runs)}: {runs}")
    return runs


def torso_anchor_x(image: Image.Image, bbox: tuple[int, int, int, int]) -> float:
    top, bottom = bbox[1], bbox[3]
    alpha = np.asarray(image.getchannel("A"))
    core_top = round(top + (bottom - top) * 0.33)
    core_bottom = round(top + (bottom - top) * 0.52)
    _, core_x = np.nonzero(alpha[core_top:core_bottom] > 128)
    return float(np.median(core_x)) if core_x.size else (bbox[0] + bbox[2]) / 2.0


def place_sprite(sprite: Image.Image, scale: float) -> Image.Image:
    scaled = sprite.resize((round(sprite.width * scale), round(sprite.height * scale)), Image.Resampling.LANCZOS)
    bbox = scaled.getchannel("A").getbbox()
    if not bbox:
        raise RuntimeError("sprite vanished during normalization")
    output = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT))
    dx = round(FRAME_WIDTH / 2.0 - torso_anchor_x(scaled, bbox))
    dy = FOOT_Y - (bbox[3] - 1)
    output.alpha_composite(scaled, (dx, dy))
    return color_match(output)


def main() -> None:
    source = remove_magenta(Image.open(SOURCE))
    runs = find_sprite_columns(source)
    splits = [0]
    splits.extend(round((runs[index][1] + runs[index + 1][0]) / 2) for index in range(FRAME_COUNT - 1))
    splits.append(source.width)

    cells: list[Image.Image] = []
    boxes: list[tuple[int, int, int, int]] = []
    for index in range(FRAME_COUNT):
        cell = keep_largest_component(source.crop((splits[index], 0, splits[index + 1], source.height)))
        bbox = cell.getchannel("A").getbbox()
        if not bbox:
            raise RuntimeError(f"relaxed walk frame {index} is empty")
        cells.append(cell)
        boxes.append(bbox)

    scale = CHARACTER_HEIGHT / max(bottom - top for _, top, _, bottom in boxes)
    frames = [place_sprite(cell, scale) for cell in cells]
    atlas = Image.new("RGBA", (FRAME_WIDTH * 4, FRAME_HEIGHT * 2))
    for index, frame in enumerate(frames):
        atlas.alpha_composite(frame, ((index % 4) * FRAME_WIDTH, (index // 4) * FRAME_HEIGHT))
    atlas.save(CHARACTER_DIR / "protagonist_side_walk_v07.png")

    idle_source = Image.open(CHARACTER_DIR / "protagonist_side_idle_v06.png").convert("RGBA")
    idle_bbox = idle_source.getchannel("A").getbbox()
    if not idle_bbox:
        raise RuntimeError("idle sprite is empty")
    idle_scale = CHARACTER_HEIGHT / (idle_bbox[3] - idle_bbox[1])
    place_sprite(idle_source, idle_scale).save(CHARACTER_DIR / "protagonist_side_idle_v07.png")

    metadata = {
        "view": "fixed_side",
        "columns": 4,
        "rows": 2,
        "frame_width": FRAME_WIDTH,
        "frame_height": FRAME_HEIGHT,
        "frame_count": FRAME_COUNT,
        "fps": FPS,
        "cycle_duration_seconds": FRAME_COUNT / FPS,
        "character_height": CHARACTER_HEIGHT,
        "foot_anchor": [FRAME_WIDTH // 2, FOOT_Y],
        "room_ground_y": 795,
        "door_ratio": 0.918,
        "motion": "relaxed small-stride daily walk with low foot clearance and restrained upper-body motion",
        "direction": "left",
        "right_direction": "horizontal flip",
        "recommended_world_speed_px_per_second": WALK_SPEED,
        "frame_order": [
            "left_contact", "left_settle", "left_pass", "left_release",
            "right_contact", "right_settle", "right_pass", "right_release",
        ],
    }
    (CHARACTER_DIR / "protagonist_side_walk_v07.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"frames": FRAME_COUNT, "fps": FPS, "atlas": list(atlas.size), "scale": round(scale, 4)}))


if __name__ == "__main__":
    main()

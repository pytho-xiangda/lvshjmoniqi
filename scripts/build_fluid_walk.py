"""Build the 12-drawing fluid walk atlas used by the Godot daily-room demo."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from build_natural_walk import keep_largest_component, remove_magenta
from build_relaxed_walk import place_sprite


ROOT = Path(__file__).resolve().parents[1]
CHARACTER_DIR = ROOT / "assets" / "art" / "daily" / "characters"
SOURCE = CHARACTER_DIR / "source_v09" / "fluid_walk_cycle_sheet.png"
FRAME_WIDTH = 448
FRAME_HEIGHT = 640
FRAME_COUNT = 12
FPS = 12


def main() -> None:
    source = remove_magenta(Image.open(SOURCE))
    cell_width = source.width // 4
    cell_height = source.height // 3
    cells: list[Image.Image] = []
    boxes: list[tuple[int, int, int, int]] = []
    for index in range(FRAME_COUNT):
        column = index % 4
        row = index // 4
        cell = source.crop(
            (
                column * cell_width,
                row * cell_height,
                source.width if column == 3 else (column + 1) * cell_width,
                source.height if row == 2 else (row + 1) * cell_height,
            )
        )
        cell = keep_largest_component(cell)
        bbox = cell.getchannel("A").getbbox()
        if not bbox:
            raise RuntimeError(f"fluid walk frame {index} is empty")
        cells.append(cell)
        boxes.append(bbox)

    scale = 540 / max(bottom - top for _, top, _, bottom in boxes)
    frames = [place_sprite(cell, scale) for cell in cells]
    atlas = Image.new("RGBA", (FRAME_WIDTH * 4, FRAME_HEIGHT * 3))
    for index, frame in enumerate(frames):
        atlas.alpha_composite(frame, ((index % 4) * FRAME_WIDTH, (index // 4) * FRAME_HEIGHT))
    atlas_path = CHARACTER_DIR / "protagonist_side_walk_v09.png"
    atlas.save(atlas_path)

    metadata = {
        "view": "fixed_side",
        "columns": 4,
        "rows": 3,
        "frame_width": FRAME_WIDTH,
        "frame_height": FRAME_HEIGHT,
        "frame_count": FRAME_COUNT,
        "fps": FPS,
        "cycle_duration_seconds": 1.0,
        "character_height": 540,
        "foot_anchor": [FRAME_WIDTH // 2, 610],
        "room_ground_y": 795,
        "motion": "twelve-drawing relaxed walk with continuous procedural weight shift in Godot",
        "direction": "left",
        "right_direction": "horizontal flip",
        "recommended_world_speed_px_per_second": 140,
    }
    (CHARACTER_DIR / "protagonist_side_walk_v09.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"frames": FRAME_COUNT, "fps": FPS, "atlas": list(atlas.size), "scale": round(scale, 4)}))


if __name__ == "__main__":
    main()

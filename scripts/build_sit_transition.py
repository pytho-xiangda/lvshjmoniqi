"""Build the seated transition atlas while preserving one physical character scale."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from build_natural_walk import keep_largest_component, remove_magenta
from build_relaxed_walk import place_sprite


ROOT = Path(__file__).resolve().parents[1]
CHARACTER_DIR = ROOT / "assets" / "art" / "daily" / "characters"
SOURCE = CHARACTER_DIR / "source_v10" / "sit_transition_sheet.png"
FRAME_WIDTH = 448
FRAME_HEIGHT = 640
FRAME_COUNT = 8


def main() -> None:
    source = remove_magenta(Image.open(SOURCE))
    cell_width = source.width // 4
    cell_height = source.height // 2
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
                source.height if row == 1 else (row + 1) * cell_height,
            )
        )
        cell = keep_largest_component(cell)
        bbox = cell.getchannel("A").getbbox()
        if not bbox:
            raise RuntimeError(f"sit frame {index} is empty")
        cells.append(cell)
        boxes.append(bbox)

    standing_height = max(boxes[0][3] - boxes[0][1], boxes[1][3] - boxes[1][1])
    scale = 540 / standing_height
    frames = [place_sprite(cell, scale) for cell in cells]
    atlas = Image.new("RGBA", (FRAME_WIDTH * 4, FRAME_HEIGHT * 2))
    for index, frame in enumerate(frames):
        atlas.alpha_composite(frame, ((index % 4) * FRAME_WIDTH, (index // 4) * FRAME_HEIGHT))
    atlas.save(CHARACTER_DIR / "protagonist_side_sit_v10.png")

    metadata = {
        "columns": 4,
        "rows": 2,
        "frame_width": FRAME_WIDTH,
        "frame_height": FRAME_HEIGHT,
        "frame_count": FRAME_COUNT,
        "fps": 8,
        "character_height_standing": 540,
        "foot_anchor": [FRAME_WIDTH // 2, 610],
        "frame_order": [
            "stand", "settle", "lower_begin", "lower_reach",
            "near_seat", "seated", "keyboard_reach", "working_idle",
        ],
    }
    (CHARACTER_DIR / "protagonist_side_sit_v10.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"frames": FRAME_COUNT, "atlas": list(atlas.size), "scale": round(scale, 4)}))


if __name__ == "__main__":
    main()

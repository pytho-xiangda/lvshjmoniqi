"""Convert the approved eight-pose walk sheet into a game-ready atlas."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

from build_smooth_side_sprites import color_match


ROOT = Path(__file__).resolve().parents[1]
CHARACTER_DIR = ROOT / "assets" / "art" / "daily" / "characters"
SOURCE = CHARACTER_DIR / "source_v06" / "walk_cycle_sheet.png"
FRAME_WIDTH = 384
FRAME_HEIGHT = 530
FRAME_COUNT = 8
FOOT_Y = 510
CHARACTER_HEIGHT = 470


def remove_magenta(image: Image.Image) -> Image.Image:
    """Remove the generated chroma matte while preserving painted edge color."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    chroma = np.minimum(rgb[..., 0] - rgb[..., 1], rgb[..., 2] - rgb[..., 1])
    magenta = (rgb[..., 0] + rgb[..., 2]) * 0.5
    alpha = np.clip(1.0 - (chroma + 2.0) / 16.0, 0.0, 1.0)
    alpha[magenta < 130.0] = 1.0

    # Edge pixels inherit the matte color. Pull color from neighbouring opaque
    # pixels before applying alpha so sprites do not show a pink fringe in game.
    filled = rgb.copy()
    valid = alpha > 0.97
    needs_color = (alpha > 0.02) & ~valid
    height, width = alpha.shape
    for _ in range(20):
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
    purple_edge = ((filled[..., 0] - filled[..., 1]) > 5.0) & ((filled[..., 2] - filled[..., 1]) > 5.0)
    edge_luminance = filled[..., 0] * 0.299 + filled[..., 1] * 0.587 + filled[..., 2] * 0.114
    filled[purple_edge, 0] = edge_luminance[purple_edge] * 1.18
    filled[purple_edge, 1] = edge_luminance[purple_edge] * 0.82
    filled[purple_edge, 2] = edge_luminance[purple_edge] * 0.62
    rgba = np.concatenate([np.clip(filled, 0, 255), alpha[..., None] * 255.0], axis=2)
    rgba[alpha < 0.025] = 0
    return Image.fromarray(rgba.astype(np.uint8), "RGBA")


def keep_largest_component(image: Image.Image) -> Image.Image:
    """Discard tiny pieces leaking across generated sprite-sheet gutters."""
    rgba = np.asarray(image).copy()
    mask = rgba[..., 3] > 20
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    largest: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            if visited[y, x] or not mask[y, x]:
                continue
            stack = [(y, x)]
            visited[y, x] = True
            component: list[tuple[int, int]] = []
            while stack:
                py, px = stack.pop()
                component.append((py, px))
                for ny in range(max(0, py - 1), min(height, py + 2)):
                    for nx in range(max(0, px - 1), min(width, px + 2)):
                        if not visited[ny, nx] and mask[ny, nx]:
                            visited[ny, nx] = True
                            stack.append((ny, nx))
            if len(component) > len(largest):
                largest = component
    keep = np.zeros_like(mask, dtype=bool)
    if largest:
        ys, xs = zip(*largest)
        keep[np.asarray(ys), np.asarray(xs)] = True
    for _ in range(2):
        expanded = keep.copy()
        expanded[1:] |= keep[:-1]
        expanded[:-1] |= keep[1:]
        expanded[:, 1:] |= keep[:, :-1]
        expanded[:, :-1] |= keep[:, 1:]
        keep = expanded
    rgba[~keep] = 0
    return Image.fromarray(rgba, "RGBA")


def main() -> None:
    source = remove_magenta(Image.open(SOURCE))
    source_width, source_height = source.size
    source_alpha = np.asarray(source.getchannel("A"))
    active_columns = (source_alpha > 20).sum(axis=0) > 30
    runs: list[tuple[int, int]] = []
    run_start: int | None = None
    for x, active in enumerate(active_columns):
        if active and run_start is None:
            run_start = x
        if run_start is not None and (not active or x == source_width - 1):
            run_end = x if not active else x + 1
            if run_end - run_start > 30:
                runs.append((run_start, run_end))
            run_start = None
    if len(runs) != FRAME_COUNT:
        raise RuntimeError(f"expected {FRAME_COUNT} character columns, found {len(runs)}: {runs}")

    splits = [0]
    splits.extend(round((runs[index][1] + runs[index + 1][0]) / 2) for index in range(FRAME_COUNT - 1))
    splits.append(source_width)
    cells: list[Image.Image] = []
    boxes: list[tuple[int, int, int, int]] = []
    for index in range(FRAME_COUNT):
        cell = keep_largest_component(source.crop((splits[index], 0, splits[index + 1], source_height)))
        bbox = cell.getchannel("A").getbbox()
        if not bbox:
            raise RuntimeError(f"walk frame {index} is empty")
        cells.append(cell)
        boxes.append(bbox)

    # One shared scale and one cell-centre body anchor preserve the generated
    # vertical rhythm and prevent changing limb silhouettes from shaking the hip.
    tallest = max(bottom - top for _, top, _, bottom in boxes)
    scale = CHARACTER_HEIGHT / tallest
    frames: list[Image.Image] = []
    frame_metrics: list[dict[str, int | float | list[int]]] = []
    for index, (cell, bbox) in enumerate(zip(cells, boxes, strict=True)):
        scaled = cell.resize((round(cell.width * scale), round(cell.height * scale)), Image.Resampling.LANCZOS)
        scaled_bbox = scaled.getchannel("A").getbbox()
        if not scaled_bbox:
            raise RuntimeError(f"walk frame {index} vanished during normalization")
        output = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT))
        top, bottom = scaled_bbox[1], scaled_bbox[3]
        alpha_array = np.asarray(scaled.getchannel("A"))
        core_top = round(top + (bottom - top) * 0.34)
        core_bottom = round(top + (bottom - top) * 0.51)
        core_y, core_x = np.nonzero(alpha_array[core_top:core_bottom] > 128)
        anchor_x = float(np.median(core_x)) if core_x.size else (scaled_bbox[0] + scaled_bbox[2]) / 2.0
        dx = round(FRAME_WIDTH / 2.0 - anchor_x)
        dy = FOOT_Y - (scaled_bbox[3] - 1)
        output.alpha_composite(scaled, (dx, dy))
        frames.append(color_match(output))
        normalized_bbox = frames[-1].getchannel("A").getbbox()
        frame_metrics.append({
            "index": index,
            "source_bbox": list(bbox),
            "normalized_bbox": list(normalized_bbox or (0, 0, 0, 0)),
            "baseline": FOOT_Y,
        })

    atlas = Image.new("RGBA", (FRAME_WIDTH * 4, FRAME_HEIGHT * 2))
    for index, frame in enumerate(frames):
        atlas.alpha_composite(frame, ((index % 4) * FRAME_WIDTH, (index // 4) * FRAME_HEIGHT))
    atlas_path = CHARACTER_DIR / "protagonist_side_walk_v06.png"
    atlas.save(atlas_path)
    color_match(Image.open(CHARACTER_DIR / "protagonist_side_idle_v03.png").convert("RGBA")).save(
        CHARACTER_DIR / "protagonist_side_idle_v06.png"
    )

    metadata = {
        "view": "fixed_side",
        "columns": 4,
        "rows": 2,
        "frame_width": FRAME_WIDTH,
        "frame_height": FRAME_HEIGHT,
        "frame_count": FRAME_COUNT,
        "fps": 10,
        "cycle_duration_seconds": 0.8,
        "character_height": CHARACTER_HEIGHT,
        "foot_anchor": [192, FOOT_Y],
        "room_ground_y": 795,
        "motion": "eight hand-painted walk phases: contact, down, passing and up for both feet",
        "direction": "left",
        "right_direction": "horizontal flip",
        "frame_order": [
            "left_contact", "left_down", "left_passing", "left_up",
            "right_contact", "right_down", "right_passing", "right_up",
        ],
        "recommended_world_speed_px_per_second": 178,
        "metrics": frame_metrics,
    }
    (CHARACTER_DIR / "protagonist_side_walk_v06.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"frames": FRAME_COUNT, "fps": 10, "atlas": list(atlas.size), "scale": round(scale, 4)}))


if __name__ == "__main__":
    main()

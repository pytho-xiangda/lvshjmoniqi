# 日常房间 v09 生成提示词

## 生成模式

参考图编辑。参考 `assets/art/daily/characters/source_v07/relaxed_walk_cycle_sheet.png`，生成同一角色的十二帧完整人物动作表；不使用骨骼拆件作为最终资产。

## 提示词

> Edit and rebuild the referenced protagonist walk-cycle sheet into a production-quality 12-frame 2D game animation atlas. Keep exactly the same young adult male protagonist, same face, dark brown tousled hair, cream rolled-sleeve shirt, charcoal high-waisted trousers, brown leather shoes, and the same warm hand-painted watercolor/gouache animation style as the reference. Fixed clean side profile facing LEFT, full body visible in every frame, tall elegant adult proportion about 7.5 heads, same height and volume in every cell. Layout: exactly 4 columns by 3 rows, twelve equal cells, no borders, no labels, no text. Solid vivid magenta chroma background only (#ff00ff), no shadow, no floor, no props. Create twelve genuinely distinct consecutive in-place walking drawings for a relaxed everyday stroll: left contact, left compression, left recoil, left passing, left high point, left reach, right contact, right compression, right recoil, right passing, right high point, right reach. Natural modest stride, low foot clearance, heel-to-toe roll, knee flexion, soft opposite arm swing, subtle shoulder and hip counter-rotation, relaxed fingers, quiet breathing, slight hair and shirt-hem follow-through. The planted foot must remain visually anchored through each contact phase. Match head position smoothly between adjacent frames; no sudden body-size jumps, no duplicated poses, no marching, no exaggerated runway stride. Crisp separated silhouette and consistent registration suitable for automatic cell extraction in Godot.

输出经 `scripts/build_fluid_walk.py` 去除色键、统一人物高度和脚底锚点，并排入 1792×1920 RGBA 图集。

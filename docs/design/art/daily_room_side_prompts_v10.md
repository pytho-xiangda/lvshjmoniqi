# 日常房间 v10 坐下动画提示词

## 生成模式

参考图编辑。参考 `assets/art/daily/characters/source_v09/fluid_walk_cycle_sheet.png`，为同一主角生成八帧站立到坐姿的完整人物动作表。

## 提示词

> Create a production-ready 8-frame seated transition animation atlas for the exact same young adult male protagonist in the reference: identical face, dark brown tousled hair, cream rolled-sleeve shirt, charcoal high-waisted trousers, brown leather shoes, same warm hand-painted watercolor/gouache game art and clean side profile facing LEFT. Exactly 4 columns by 2 rows, eight equal cells, no borders, labels or text. Solid vivid magenta chroma background only (#ff00ff), no room, no chair, no desk, no props, no shadows. Full body visible in every cell at one consistent physical scale and line weight. Sequential action: 1 standing relaxed, 2 brief settling breath, 3 hips begin lowering and torso leans slightly forward, 4 knees bend naturally and hands start reaching toward desk height, 5 near-seat with controlled weight, 6 seated side pose with thighs nearly horizontal and feet planted, 7 seated hands forward as if reaching a keyboard, 8 relaxed seated working idle. Preserve foot contact and believable balance. Smooth anticipation and follow-through, calm everyday movement, no dramatic squat, no floating, no body-size jumps, no duplicated frames, no chair drawn into the character, suitable for transparent sprite extraction and crossfade animation in Godot.

输出由 `scripts/build_sit_transition.py` 去除色键，并使用站立帧确定统一物理缩放；坐姿帧不会被单独放大。

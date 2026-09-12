# 横版日常房间 v03 · 生成提示词

工具：内置 imagegen。所有输出均先保存到内置生成目录，再复制到项目。生成器把人物背景输出为 RGB 棋盘格，因此最终游戏图集通过项目内脚本进行连通背景抠除和统一锚点对齐；没有把棋盘格当作透明通道。

## 横版房间背景

参考图 1：`assets/art/main_menu_concept.png`（美术基准）；参考图 2：`assets/art/daily/daily_room_warm_v02.png`（陈设内容参考）。

Use case: stylized-concept
Asset type: production-ready 2D side-scrolling game environment background for Godot, not a poster, not a room photograph, not an isometric scene.
Input images: Image 1 is the approved warm hand-painted watercolor and brown-pencil art direction reference; Image 2 is the previous room content reference only.
Primary request: rebuild the young Chinese lawyer's daily home-office as a true horizontal side-view playable room.
Scene/backdrop: a contemporary modest apartment in an older Chinese neighborhood, warm afternoon, old walnut furniture, cream plaster, plants, books and case files, with a current-era thin 24-inch dark LCD monitor, slim keyboard, ordinary mouse and small tower under the desk.
Style/medium: original 2D animated-game background, hand-painted watercolor/gouache on subtle paper with clean brown pencil contours; simplified readable shapes and controlled detail matching Image 1, no photorealism, no 3D render.
Composition/framing: single fixed orthographic side elevation / dollhouse cutaway, 16:9 landscape. Back wall is almost flat to camera. The entire floor edge is a perfectly horizontal baseline across the lower 23% and forms one unobstructed left-right walk lane. No vanishing-point depth and no diagonal floorboards. The room must read as a platform-adventure gameplay screen at thumbnail size.
Layout: desk and current-era computer against the LEFT wall, with the chair tucked close enough that the walk lane stays clear; a broad bright window above/behind the desk. Low bookcase, wall notes and a reading nook sit in the middle background. A full-height wooden exit door with frosted upper glass is on the far RIGHT and fully visible from lintel to floor. Keep an empty character interaction point in front of the desk and another in front of the door.
Scale system: door opening equals 220 cm; desk height equals about 75 cm; chair seat about 45 cm. A 175 cm adult would appear at exactly 80% of the visible door opening height and stand with both feet on the same floor baseline. Do not include the character, but compose all props to this scale.
Lighting/mood: warm calm daylight from upper left, restrained highlights, gentle domestic beauty.
Constraints: empty room background only; no people; no UI; no labels; no readable text; no logo; no border; no giant foreground furniture; do not obstruct the horizontal walk lane; every object uses the same side-view projection and painterly line language.
Avoid: perspective room photography, wide-angle lens, three-quarter view, top-down view, isometric view, cinematic concept-art camera, glossy realism, detailed architectural visualization, CRT monitor, laptop, futuristic gaming PC, visual clutter on the walk lane.

## 六帧图集修订尝试

此稿用于锁定人物线条和服装，最终动画没有直接采用整张六帧图集，而是改为逐个关键帧生成后组装。

Use case: identity-preserve
Asset type: corrected production 2D game walk-cycle atlas.
Input images: Image 1 is the edit target and character drawing anchor; Image 2 is the approved protagonist identity; Image 3 is the exact side-view room style and scale reference.
Primary request: redraw the atlas as exactly SIX mechanically correct small-step walking frames for the same male protagonist, facing LEFT. Repair the gait while preserving his face, hair, outfit, proportions, warm-brown pencil line and restrained watercolor rendering.
Layout: strict 3 columns × 2 rows of equal cells, read left-to-right then top-to-bottom. One full body per cell. Same head top, shoulder width, pelvis height, trouser length and sole baseline in all six frames. Figures centered with full shoes and generous empty padding; do not touch adjacent cells.
Six-frame loop:
1 LEFT heel contacts ground about half a foot-length ahead of pelvis; RIGHT toe touches ground about half a foot-length behind.
2 LEFT foot flat under front hip carrying weight; RIGHT foot lifts only 2–3 cm and begins passing; both knees softly bent.
3 RIGHT foot passes directly under pelvis with knee mildly bent; LEFT heel starts lifting; body at normal height.
4 Mirror of frame 1: RIGHT heel contacts half a foot-length ahead; LEFT toe touches half a foot-length behind.
5 Mirror of frame 2: RIGHT foot flat carrying weight; LEFT foot lifts only 2–3 cm and begins passing.
6 Mirror of frame 3: LEFT foot passes under pelvis; RIGHT heel starts lifting.
Motion rules: everyday indoor pace, total front-to-back foot spread never exceeds one shoulder width; torso vertical; head level within 2%; hips level; no crouch; no leaning; no airborne phase; no foot higher than ankle; arms counter-swing subtly within 10 degrees; elbows relaxed; hands open and anatomical.
Style matching: use Image 3's simplified 2D game-painting finish, line weight, contrast and warm ambient light. Character should visually belong inside Image 3, not look like glossy anime key art.
Backdrop: genuinely transparent alpha around all figures.
Constraints: exact same character in every cell; white rolled-sleeve shirt, charcoal straight trousers, brown leather shoes, empty hands. No cast shadow, floor, frame lines, labels, numbers, text, logo or watermark.
Avoid: long stride, straight split legs, marching, running, crouching, lunging, floating, crossed legs, twisted pelvis, changing face, changing sleeve length, painted checkerboard or paper background.

## 四个行走关键帧

四次内置 imagegen 调用共享以下提示：

Use case: identity-preserve
Asset type: one key frame for a production 2D side-view game walk cycle.
Input images: Image 1 is the approved male protagonist identity and outfit reference; Image 2 is the corrected character drawing/line-quality anchor; Image 3 is the exact horizontal room style and scale reference.
Subject: the SAME young adult Chinese male protagonist, true LEFT-facing profile, full body, empty hands, messy short dark-brown hair, ivory rolled-sleeve shirt tucked into charcoal straight trousers, brown leather shoes, natural 7.5-head adult proportions.
Style/medium: exactly match the warm-brown pencil contour, restrained watercolor/gouache fill, edge sharpness, contrast and warm ambient light of Image 3; production game sprite, not glossy anime key art.
Camera/registration: orthographic side view, torso upright, head level, pelvis level, sole baseline horizontal, full shoes visible, ample transparent padding.
Motion quality: quiet indoor walking at normal pace, step spread no wider than shoulders, knees soft, heel-to-toe weight, no crouch, no lunge, no running, no marching, no leaning, no airborne phase; arms counter-swing at most 10 degrees with relaxed elbows and natural open hands.
Backdrop: genuinely transparent alpha.
Constraints: exactly ONE figure only; no cast shadow, floor, checkerboard, paper backdrop, cell line, label, number, text, logo or watermark. Preserve identity, hair, sleeve length, belt, trouser width, shoes and lighting.

每次调用分别追加：

1. KEY FRAME A — LEFT heel contact. The LEFT leg reaches only half a foot-length forward and its heel touches the baseline. The RIGHT leg trails half a foot-length backward with toe touching.
2. KEY FRAME B — RIGHT leg passing. LEFT foot is flat under the pelvis. The RIGHT leg passes forward under the pelvis with a mild knee bend and a 2 cm lift.
3. KEY FRAME C — RIGHT heel contact, the clear opposite of A. The RIGHT heel touches ahead while the LEFT toe remains behind.
4. KEY FRAME D — LEFT leg passing, the clear opposite of B. RIGHT foot carries weight while the LEFT leg passes under the pelvis.

## 独立待机帧

Use case: identity-preserve
Asset type: production 2D side-view game idle sprite.
Input images: Image 1 is the approved male protagonist identity reference; Image 2 is the new horizontal room style and scale reference; Image 3 is the latest walk key-frame drawing anchor.
Primary request: the SAME young adult Chinese male protagonist standing naturally at rest, facing LEFT, full body, ready for a quiet indoor game scene.
Subject: messy short dark-brown hair, ivory rolled-sleeve shirt tucked into charcoal straight trousers, brown leather shoes, empty hands, natural 7.5-head adult proportions.
Pose: torso vertical, head level, shoulders relaxed, arms hanging naturally with tiny elbow bend, hands open, both shoes flat on one perfectly horizontal sole baseline, feet separated only half a shoe length, no contrapposto, no crossed legs, no walking or action pose.
Style/medium: exactly match Image 2's warm-brown pencil contours, restrained watercolor/gouache fill, edge sharpness, contrast and warm ambient light; visually belongs inside the room.
Composition: exactly ONE full figure centered with generous padding, orthographic true side profile with slight chest visibility.
Backdrop: genuinely transparent alpha.
Constraints: preserve face, hair, shirt, sleeve length, belt, trouser width and shoes; no bag, folder, coat, cast shadow, floor, checkerboard, paper backdrop, text, logo or watermark.
Avoid: glossy anime key art, portrait crop, walking pose, raised heel, bent knee, lean, slouch or oversized head.

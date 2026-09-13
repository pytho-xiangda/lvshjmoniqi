# 横版日常房间 v04 · 风格修订提示词

工具：内置 imagegen 图片编辑。

输入图 1：`assets/art/daily/daily_room_side_v03.png`，编辑目标；输入图 2：`assets/art/daily/daily_room_side_character_preview_v03.png`，人物与环境匹配参考；输入图 3：`assets/art/main_menu_concept.png`，全局美术基准。

Use case: style-transfer
Asset type: final production 2D side-scrolling game room background, versioned refinement.
Input images: Image 1 is the edit target and its exact geometry/layout must be preserved; Image 2 shows the actual protagonist composited in the room and is the matching target for line weight, paint density and character readability; Image 3 is the approved overall game art-direction reference.
Primary request: restyle ONLY the empty room background so the protagonist from Image 2 feels painted by the same artist and does not look pasted on.
Preserve exactly: fixed orthographic side elevation, 1672×941 landscape composition, horizontal floor/walk lane, modern thin-screen computer and desk on the left, bookcases and low cabinet in the middle, full wooden exit door on the right, all interaction clearances and object scale. Keep the room empty with no people.
Style adjustment: simplify background micro-detail by about 25%; group books, foliage and wood grain into larger readable hand-painted shapes; replace architectural-render precision with restrained watercolor/gouache washes and warm-brown pencil contours matching the protagonist. Use the same moderate edge softness, paper grain, contrast and shadow density as the character. Keep foreground furniture silhouettes crisp enough for gameplay, while reducing tiny decorative line noise behind the walk lane.
Color integration: slightly cool and desaturate the strongest orange floor highlights; keep cream wall, walnut wood, sage green and sky blue. Use a restrained warm ambient wash so the protagonist's ivory shirt and charcoal trousers sit naturally in the room.
Game readability: maintain a quiet value band across the horizontal walk lane; keep the desk and door readable at thumbnail size; leave room for engine UI. This must look like a painted 2D adventure-game background, not an interior photo, not an architectural visualization, not a poster.
Constraints: change style and paint treatment only; do not move, add, remove or redesign furniture; do not change the computer into a CRT or laptop; no people, UI, buttons, labels, readable text, logo, border or watermark; no depth scaling, diagonal camera or isometric view.
Avoid: photorealism, hyper-detailed book spines, hard photographic textures, glossy 3D materials, excessive golden bloom, anime cel shading, flat vector art.

人物没有重新生成。v04 使用 v03 的四张独立关键姿势与待机帧，通过 `scripts/build_smooth_side_sprites.py` 统一环境色并离线生成中间帧。

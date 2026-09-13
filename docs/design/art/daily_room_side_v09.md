# 横版日常房间 v09 · 连续动画版

v09 是当前 Godot 日常房间基准。它保留暖色手绘横版场景和修长成年主角，将行走升级为十二张完整人物绘制，并用连续步态相位同步位移、重心起伏、轻微肩胯旋转和落脚缓冲。运行画面保持 30/60 fps 连续更新，避免整张人物图只做匀速平移。

## 人物动画

- 图集为 4 列 × 3 行、12 张完整绘制、12 fps，完整循环约 1 秒。
- 十二阶段覆盖左右脚的接触、承重、回弹、经过、高点和前伸。
- 人物高度 540 px，脚底锚点 `(224,610)`，场景地面基线 `y=795`。
- 水平速度 140 px/s，加速度 310 px/s²；动画相位按实际移动距离推进，启动和制动时步频同步变化。
- Godot 每帧额外计算 3.4 px 以内的重心起伏、约 0.28° 的肩胯转动和极轻的落地压缩。
- 停步后切换完整待机帧，并保留呼吸和身体微摆。

## 全场景律动

- 左右窗帘、吊灯、窗外枝叶和室内植物使用不同频率、不同相位的低幅摆动。
- 云影缓慢横穿地面，窗边暖光以长周期呼吸变化。
- 两层浮尘分别做漂移和上升，避免粒子同步。
- 电脑屏幕呼吸光、时钟秒针和人物跟随阴影持续运行。
- 动态层的振幅和透明度保持克制，交互按钮、电脑桌、门口与人物轮廓始终清晰。

## 交互与资源

- 场景启动后人物从门口走向电脑桌；点击地板或右上角按钮可改变目标。
- `Space` 重播，`Esc` 退出；抵达电脑桌或门口显示行动面板。
- 主场景：`scenes/daily_room_demo.tscn`
- 控制脚本：`scripts/daily_room_demo.gd`
- 环境动画：`scripts/daily_room_ambient.gd`
- 行走图集：`assets/art/daily/characters/protagonist_side_walk_v09.png`
- 动画数据：`assets/art/daily/characters/protagonist_side_walk_v09.json`
- 原始动作表：`assets/art/daily/characters/source_v09/fluid_walk_cycle_sheet.png`
- Godot 实录：`assets/videos/daily_room_godot_demo_v09.mp4`
- Godot 截图：`assets/art/daily/daily_room_godot_preview_v09.png`

## 验证

本机 Godot 4.7.1 使用 OpenGL Compatibility 和 Movie Maker 实际渲染 223 帧、30 fps、约 7.43 秒。视频转为 H.264 MP4 后完成全片解码和 4 fps 接触表检查，未发现 GDScript 解析或运行错误。

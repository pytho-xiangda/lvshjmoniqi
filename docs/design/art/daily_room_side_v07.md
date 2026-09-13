# 横版日常房间 v07 · Godot 轻松步态演示

v07 已作为可运行场景接入 Godot 4.7.1。主场景是 `scenes/daily_room_demo.tscn`，工程入口是 `project.godot`。背景继续使用 `assets/art/daily/daily_room_side_v04.png`，人物与环境使用同一套暖色水彩、棕色铅笔线和纸张肌理。

## 人物比例与步态

- 人物高度 540 px，约为可见门洞高度的 91.8%，保持修长的成年人比例。
- 帧尺寸 448×640，脚底锚点 (224,610)，地面基线 y=795。
- 行走图集为 4 列 × 2 行、8 帧、8 fps；完整循环 1 秒。
- 移动速度 140 px/s，加速度 310 px/s²；起步和停步使用逐渐加减速，避免机械瞬移。
- 动作采用较小的日常步幅、低抬脚、轻微屈膝和收敛的反向摆臂；头部高度基本稳定。
- 左行使用原图，右行由 `AnimatedSprite2D.flip_h` 水平翻转。

## 场景活动

Godot 运行时通过 `scripts/daily_room_ambient.gd` 和 `scripts/daily_room_demo.gd` 提供以下循环动态：

- 左右窗帘以不同频率轻摆。
- 窗外树叶与室内植物轻微错相摆动。
- 地面叶影缓慢漂移，阳光尘埃分层浮动。
- 电脑屏幕做低亮度呼吸光。
- 墙上时钟秒针持续行走。
- 人物脚下阴影跟随水平位置。

这些运动保持低对比度和低振幅，让房间有呼吸感，同时不干扰电脑、门口和人物的交互识别。

## 交互

- 场景启动后，人物从门口稍作停留，再自然走向电脑桌。
- 点击前景地板可以改变目标位置。
- 右上角“去电脑桌”“去门口”按钮用于快速演示。
- 按 `Space` 重新播放门口到电脑桌流程，按 `Esc` 退出。
- 到达电脑或门口后显示相应行动面板。

## 资源

- Godot 场景：`scenes/daily_room_demo.tscn`
- 主控制脚本：`scripts/daily_room_demo.gd`
- 环境动态脚本：`scripts/daily_room_ambient.gd`
- 行走图集：`assets/art/daily/characters/protagonist_side_walk_v07.png`，1792×1280，RGBA
- 待机帧：`assets/art/daily/characters/protagonist_side_idle_v07.png`，448×640，RGBA
- 动画数据：`assets/art/daily/characters/protagonist_side_walk_v07.json`
- 原始原画：`assets/art/daily/characters/source_v07/relaxed_walk_cycle_sheet.png`
- Godot 实录：`assets/videos/daily_room_godot_demo_v07.mp4`，1280×720，30 fps
- Godot 截图：`assets/art/daily/daily_room_godot_preview_v07.png`

## 验证

已使用本机 Godot 4.7.1 完成资源导入和实际运行。Godot Movie Maker 使用 OpenGL Compatibility 渲染 223 帧，时长约 7.43 秒，未报告 GDScript 解析或运行错误；输出视频已用 FFmpeg 完整解码验证。Godot AI MCP 3.1.5 已用于打开和启动场景，插件作为本机开发工具保留，不随游戏资源提交。

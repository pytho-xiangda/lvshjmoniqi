# 横版日常房间 v03 · 当前游戏场景规范

当前背景：`assets/art/daily/daily_room_side_v03.png`，1672×941，RGB PNG。v01/v02 是三分之四透视草案；v03 改为固定正侧视，作为当前接入版本。

## 为什么重做

旧版背景存在透视纵深，而人物是正侧视平面图，移动时需要改变比例，导致画风割裂、身高不稳定和脚底滑动。v03 将墙面、家具、门、人物全部放在同一侧视投影中，地面只使用一条水平运动基线。人物左右移动时不缩放，右行通过水平翻转完成。

## 场景坐标与比例

- 原始画布：1672×941；接入时保持纵横比。
- 水平地面锚点：y=795；角色脚底始终落在该线上。
- 门口交互点：x=1360；电脑交互点：x=650；允许移动范围 x=560–1420。
- 可见门洞约 588 px；人物绘制高度固定 470 px，人物／门洞比例为 0.799，约对应 175 cm 成人与 220 cm 门洞。
- 角色不使用景深缩放。移动速度原型为 140 px/s，四帧循环 7 fps。

背景左侧是当代窄边薄屏办公电脑、键盘、鼠标与桌下主机；右侧为完整木门。桌椅、书柜和植物贴近后墙，y>705 的前景地板保持连续，供横版角色移动。

## 当前素材

- 空背景：`assets/art/daily/daily_room_side_v03.png`。
- 行走图集：`assets/art/daily/characters/protagonist_side_walk_v03.png`，1536×530，RGBA，4 列 × 1 行；单帧 384×530，角色高 470，脚底锚点 (192,510)。
- 待机帧：`assets/art/daily/characters/protagonist_side_idle_v03.png`，384×530，RGBA；双脚落地，不用跨步帧代替待机。
- 切帧元数据：`assets/art/daily/characters/protagonist_side_walk_v03.json`。
- 生成原稿：`assets/art/daily/characters/source_v03/`。每个关键姿势独立生成，便于替换单帧。
- 入景静帧：`assets/art/daily/daily_room_side_character_preview_v03.png`。
- 行走视频：`assets/videos/daily_room_side_walk_v03.mp4`，1280×720，16 fps，6 秒，无音轨。
- 可交互预览：`docs/design/art/daily_room_side_preview.html`。支持门口到电脑、电脑与门口菜单、左右行走，以及点击地板设置水平目标。

人物原稿实际为 RGB 棋盘格。`scripts/export_daily_room_side_preview.cjs` 调用预览中的连通背景抠除流程，保留最大人物轮廓，统一身高、腰部水平位置和脚底锚点后导出真实 RGBA 图集。背景与人物始终是独立文件。

## Godot 接入建议

使用 `Node2D` 作为房间根节点，背景为 `Sprite2D`，主角为 `CharacterBody2D + AnimatedSprite2D`。角色位置固定在 y=795 对应的世界线，只修改 x；左右边界为 560 和 1420。图集按 384×530 切成四帧，`walk` 设 7 fps 循环，停止时切到独立 `idle`。向右移动时设置 `flip_h=true`。

电脑与门分别使用 `Area2D`，到达 x=650 或 x=1360 后才打开界面。原型选项仍沿用“整理卷宗／检索法条／查看来信”和“律所公共区／法院／街区”，正式游戏由章节状态提供可用项。

当前仓库没有 `project.godot`，因此没有提交不可验证的 `.tscn` 或 `.tres`。坐下、起身、椅背前景遮挡及真实场景切换尚未完成；本轮解决横版投影、画风统一、人物比例、自然待机和门口到电脑的水平行走。

## 验证

导出器检查固定侧视投影、角色高度 470、人物／门洞比例 0.799、4 帧 7 fps、电脑菜单、门口菜单、重复点击、窄屏布局和页面脚本错误。FFmpeg 完整解码 96 帧视频；门口、中段和桌前三处静帧均检查脚底、比例与遮挡。完整生成提示词见 `daily_room_side_prompts_v03.md`。

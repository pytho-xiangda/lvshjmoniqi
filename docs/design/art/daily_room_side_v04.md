# 横版日常房间 v04 · 风格与动态修订

当前背景：`assets/art/daily/daily_room_side_v04.png`，1672×941。它保留 v03 的固定侧视布局和交互坐标，将书籍、木纹、植物与高光概括为更大的水彩色块，降低建筑效果图感，使人物与场景的线条密度接近。

## 游戏坐标

- 地面基线 y=795；角色位置只改变 x，不做透视缩放。
- 门口 x=1360，电脑 x=650，可移动范围 x=560–1420。
- 人物固定高度 470 px，约为可见门洞高度的 79.9%。
- 向左使用原图，向右使用水平翻转。
- 点击前景地板可以设置水平目标；只有到达电脑或房门交互点后才打开菜单。

## 动画资源

- 行走图集：`assets/art/daily/characters/protagonist_side_walk_v04.png`，2304×1060，RGBA，6 列 × 2 行。
- 单帧：384×530；12 帧循环，12 fps；脚底锚点 (192,510)。
- 待机：`assets/art/daily/characters/protagonist_side_idle_v04.png`，独立双脚落地帧。
- 元数据：`assets/art/daily/characters/protagonist_side_walk_v04.json`。
- 场景动画：`assets/videos/daily_room_side_walk_v04.mp4`，1280×720，24 fps，6 秒，无音轨。
- 入景静帧：`assets/art/daily/daily_room_side_character_preview_v04.png`。
- 可交互预览：`docs/design/art/daily_room_side_preview.html`。

四张手绘关键姿势先统一降低饱和度与对比度，并加入克制的胡桃木环境色；随后使用双向运动补偿生成 12 帧循环。补帧过程使用临时色键，最终通过透明度估计与邻近实体颜色回填清除色边，输出真实 RGBA。构建脚本为 `scripts/build_smooth_side_sprites.py`。

场景渲染器持续更新人物水平位置，行走姿势按 12 fps 播放，视频按 24 fps 输出。窗边增加低透明度光斑漂移与尘埃运动，幅度较小，不影响电脑、门和人物的交互识别。

## 复现

先构建人物图集：

`python scripts/build_smooth_side_sprites.py --ffmpeg <ffmpeg路径>`

再导出交互截图和视频：

`node scripts/export_daily_room_side_preview.cjs --video --ffmpeg <ffmpeg路径>`

## 验证与边界

已检查 12 帧图集透明通道、连续场景帧、脚底基线、固定身高、电脑与门口菜单、重复点击和窄屏布局。FFmpeg 可完整解码 144 帧视频，页面无脚本错误。

当前仓库仍没有 `project.godot`，因此没有提交不可运行验证的 Godot 场景。坐下、起身、椅背前景遮挡和正式场景切换仍需在工程入口建立后实现。

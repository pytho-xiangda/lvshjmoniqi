# 横版日常房间 v06 · 自然行走循环

当前场景继续使用 `assets/art/daily/daily_room_side_v04.png` 作为固定侧视背景。v06 只重做人物行走动画和位移节奏，解决人物像被整体平移、腿部缺少经过相的问题。

## 游戏坐标

- 地面基线 y=795；人物只沿 x 轴移动，不做透视缩放。
- 门口 x=1360，电脑 x=650，可移动范围 x=560–1420。
- 人物显示高度 470 px，约为可见门洞高度的 79.9%。
- 左行使用原图，右行在引擎中水平翻转。
- 预览移动速度为 178 px/s，完整循环 0.8 秒，使落脚节奏与场景位移接近同一自然步幅。

## 行走动作

行走循环包含左右脚各四个阶段，共八张独立原画：

1. `contact`：脚跟接触地面，另一只脚脚尖蹬地。
2. `down`：承重腿屈膝，下沉吸收重量。
3. `passing`：摆动腿屈膝从身体下方经过。
4. `up`：身体抬高，摆动腿向前送，支撑脚脚跟离地。

双臂与双腿反向摆动，肩线和骨盆有轻微反向扭转。每帧使用统一躯干锚点、统一缩放和脚底基线，避免轮廓宽度变化带来人物横向抖动。图集由独立原画清理得到，没有使用光流补帧或同一身体分块旋转。

## 资源

- 行走图集：`assets/art/daily/characters/protagonist_side_walk_v06.png`，1536×1060，RGBA，4 列 × 2 行。
- 单帧：384×530；8 帧循环，10 fps；脚底锚点 (192,510)。
- 待机：`assets/art/daily/characters/protagonist_side_idle_v06.png`。
- 元数据：`assets/art/daily/characters/protagonist_side_walk_v06.json`。
- 原始八阶段原画：`assets/art/daily/characters/source_v06/walk_cycle_sheet.png`。
- 入景静帧：`assets/art/daily/daily_room_side_character_preview_v06.png`。
- 场景动画：`assets/videos/daily_room_side_walk_v06.mp4`，1280×720，24 fps，6 秒，无音轨。
- 可交互预览：`docs/design/art/daily_room_side_preview.html`。

## 复现与接入

先构建透明图集：

`python scripts/build_natural_walk.py`

再导出交互截图和视频：

`node scripts/export_daily_room_side_preview.cjs --video --ffmpeg <ffmpeg路径>`

Godot 中建议用 `AnimatedSprite2D` 按元数据切分 4×2 图集，动画速度设为 10 fps，循环开启；角色行走速度设为 178 px/s，停止时切换独立待机帧。场景仍未创建 `project.godot`，因此当前提供的是可直接接入的素材、数据和浏览器交互原型。

## 验证

已检查图集尺寸、透明通道、八阶段顺序、统一地面锚点、角色固定身高、24 fps 场景导出、电脑和门口交互、重复点击与窄屏布局。浏览器预览未产生脚本错误。

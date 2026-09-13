# 横版日常房间 v10 · 演出时间轴版

v10 参考 `D:/dsh/silky_scene_demo` 的运行机制重新组织日常房间。参考工程只作为实现样例读取；当前项目仍使用自己的水彩场景、人物素材和交互结构。

## 连续行走

- 所有可见水平位移由 `Tween` 使用 `TRANS_SINE + EASE_IN_OUT` 完成。直接位置赋值仅用于黑场中的演出复位。
- `scripts/daily_room_character.gd` 每帧计算角色真实位移，并按实际移动距离推进十二帧步态相位。起步与制动时步频自动放慢，巡航时恢复正常。
- 一个完整步态循环对应 140 px 实际路程；落脚信号按左右半周期触发，用于同步阴影压缩和后续脚步音效。
- 待机、行走、坐下和坐姿待机使用两层 `AnimatedSprite2D` 做 0.22–0.32 秒正弦交叉淡化。

## 演出节奏

1. 黑场复位后用 0.62 秒淡入。
2. 起步前停顿 0.32 秒，再做 0.37 秒轻微下沉与释放。
3. 角色 Tween 走向电脑桌；动画相位、落脚事件和镜头跟拍同时运行。
4. 椅子前停顿 0.4 秒。
5. 八帧坐下动画播放时，角色位置同时向椅面贴合，避免走完后硬切坐姿。
6. 坐稳后电脑屏幕渐亮，相机用 1.6 秒缓慢推近并变焦到 1.16。
7. 行动面板在镜头收稳后显示。

## 相机与环境

- `Camera2D.position_smoothing_enabled` 已开启，平滑速度 4.2。
- 走动镜头采用比角色更长的 Tween，形成轻微滞后；落座后推近电脑区域。
- 窗帘、吊灯、枝叶、植物、云影、光照和浮尘继续使用不同周期运动。
- 电脑亮屏、人物阴影和落脚脉冲由 `scripts/daily_room_ambient.gd` 响应演出信号。

## 资源

- 角色控制器：`scripts/daily_room_character.gd`
- 场景与演出：`scripts/daily_room_demo.gd`
- 环境反馈：`scripts/daily_room_ambient.gd`
- 行走图集：`assets/art/daily/characters/protagonist_side_walk_v09.png`
- 坐下图集：`assets/art/daily/characters/protagonist_side_sit_v10.png`
- 坐下原画：`assets/art/daily/characters/source_v10/sit_transition_sheet.png`
- Godot 实录：`assets/videos/daily_room_godot_demo_v10.mp4`
- Godot 截图：`assets/art/daily/daily_room_godot_preview_v10.png`

## 验证

本机 Godot 4.7.1 使用 OpenGL Compatibility 和 Movie Maker 实际渲染 373 帧、30 fps、约 12.43 秒。最终 H.264 MP4 已完成全片解码；Godot 导入与运行未报告 GDScript 错误。

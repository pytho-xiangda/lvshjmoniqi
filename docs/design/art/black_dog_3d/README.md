# 黑狗 3D 游戏资产 · v01

> 当前成年犬使用 [v03 长毛剪影修订版](v03/README.md)，幼犬保留 [v02 游戏模型](v02/README.md)。以下为 v01 历史记录；默认 Godot 预览与测试使用上述组合。

按已确认的幼犬/成年三视图制作，保留黑色躯体、圆垂耳、白下巴胸斑、大眼与上卷尾。该版采用简化的实体毛簇和圆润表面，适合风格化 3D 角色；不包含插画级毛丝、毛发模拟或写实皮毛贴图。

## 交付

| 阶段 | Godot / glTF 2.0 文件 | Blender 可编辑源文件 | 三角面 | 高度 |
|---|---|---|---:|---:|
| 幼犬 | `assets/models/black_dog/puppy_black_dog_v01.glb` | `art_source/black_dog/puppy_black_dog_v01.blend` | 24,558 | 0.3436 m |
| 成年 | `assets/models/black_dog/adult_black_dog_v01.glb` | `art_source/black_dog/adult_black_dog_v01.blend` | 23,384 | 0.7183 m |

尺寸为游戏用视觉设定，不代表照片中犬只的实际成年身高预测。每个版本一个蒙皮网格、6 个材质 surface、29 根骨骼，最多 4 权重/顶点，权重归一化，无未绑定顶点。包含 UV 展开；颜色主要由材质和顶点色承载，没有外部纹理依赖。

`.blend` 在带 `.gdignore` 的 `art_source/` 中，避免 Godot 自动调用 Blender 重复导入；游戏直接使用 `.glb`。源文件带渲染灯光、地面和相机，GLB 仅导出角色与骨骼。

Godot 4.7.1 实测导入时首个材质未开启顶点色显示。两份 `.glb.import` 已挂接 `scripts/black_dog_import.gd`，在导入阶段启用顶点色，避免身体变白。迁移到其他 Godot 工程时，应一同复制该脚本及导入配置；GLB 中保留了标准 `COLOR_0` 数据。

## 骨骼和动画

- 根/躯干：`root` → `pelvis` → `spine` → `chest` → `neck` → `head`；`jaw` 随头部。
- 四肢：`front.L` / `front.R` / `hind.L` / `hind.R`，各有 `.upper`、`.lower`、`.paw`。
- 耳朵：`ear.L.base`、`ear.L.tip`、`ear.R.base`、`ear.R.tip`。
- 尾巴：`tail.00` 至 `tail.05`。

这是一套可直接关键帧编辑的 FK 变形骨架，不含 IK 控制器或自动步态系统。两阶段骨名和层级一致，但静止姿势/骨长各自独立；重新定向动作时须按阶段检查，不能直接互换 inverse bind matrices。

`Idle` 与 `TailWag` 都为 30 fps、2 秒循环设计，分别提供轻微头耳活动和明显摆尾。Godot `AnimationPlayer` 内可直接播放；预览脚本设置 `Animation.LOOP_LINEAR`。在其他场景使用时，也需将循环模式设为 Linear。没有行走、奔跑、碰撞体、导航或角色控制器，后续可在此骨架上制作。

Blender 中用 Pose Mode 编辑骨骼；NLA 中启用一个动作轨道即可预览，避免两条轨道同时叠加。世界单位为米，Blender Z 向上、朝 -Y，导出自动转为 glTF/Godot Y 向上、朝 +Z；脚底锚点接近原点地平面。

## 配色

沿用 `black_dog_character.md`：黑毛 `#1B1716`、暖高光 `#3A2A24`、眼棕 `#5A3D2A`、眼部反光 `#7FB6D8`、白毛 `#E9DDC9`、鼻与深轮廓 `#0E0D0D`。这些是 sRGB 材质目标值；光照、色调映射和高光会影响最终渲染，截图像素不等于材质 HEX。

## Godot 使用

打开 `scenes/black_dog_3d_preview.tscn`，按 F6。按钮可切换幼犬/成年、待机/摆尾、正侧背视角与自动旋转。项目的 2D 主场景保持原入口；此资产检查场景不修改游戏系统。

正式场景可将 GLB 拖入 `Node3D`；需要在现有 2D 游戏显示时，可放入 `SubViewport` 后通过 `SubViewportContainer` / `ViewportTexture` 显示，或在 Blender 预渲染为帧动画。

## 验证和复现

生成脚本：`scripts/build_black_dog_3d.py`。使用 Blender 5.0.1 的内置 Python，无第三方 Python 依赖。该脚本会清理当前活动场景，应以独立后台进程运行：

```text
blender --background --factory-startup --python scripts/build_black_dog_3d.py
godot --headless --editor --import --quit
godot --headless --script res://tests/validate_black_dog_3d.gd --quit-after 120
```

- `puppy_mesh_validation.json`、`adult_mesh_validation.json`：面数、权重与关节变形有限性检查。
- `godot_validation.json`：Godot 4.7.1 实际导入、蒙皮、骨骼、动作与姿态变化检查。
- `*_beauty.png`、`*_front.png`、`*_side.png`、`*_back.png`：Blender 实际渲染。
- `*_pose_check.png`：抬爪、头部倾斜、耳尾活动的检查姿态。
- `*_godot.png`：Godot 预览场景实际渲染。

Blender MCP 已在本机注册并成功执行场景查询与成品加载，成品另放在 `BlackDog_GameAsset_Review` 场景。机器特定连接配置不纳入仓库。

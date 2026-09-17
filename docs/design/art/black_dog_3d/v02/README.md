# 黑狗游戏模型 v02

2026-09-17。按用户反馈重做，方向为「贴近原照片的毛茸茸小黑狗，适度卡通化」。保留垂耳、黑毛、白下巴胸斑与上卷尾；重新制作头脸、贴面眼睛、口鼻、肩腿与耳廓，不覆盖 v01 文件。

## 文件

| 阶段 | 游戏模型 | Blender 源文件 | 三角面 | 骨骼 | 身高 |
|---|---|---|---:|---:|---:|
| 幼犬 | `assets/models/black_dog/v02/puppy_black_dog_v02.glb` | `art_source/black_dog/v02/puppy_black_dog_v02.blend` | 47,757 | 29 | 0.3178 m |
| 成年 | `assets/models/black_dog/v02/adult_black_dog_v02.glb` | `art_source/black_dog/v02/adult_black_dog_v02.blend` | 47,788 | 29 | 0.7334 m |

尺寸为游戏设定，成年外观为设计推演，不是实际生长预测。每套模型一个蒙皮网格、3 个材质、每顶点最多 4 根骨骼影响，权重归一化。面数含毛发卡片，面向桌面近景宠物资产；未做移动端性能承诺或手工 LOD。

每套 GLB 内嵌一张 2048×2048 基色图、一张 128×256 毛发透明图，无外部贴图路径依赖。旁边另附 PNG 供编辑。源文件也已打包贴图。

`art_source/black_dog/v02/black_dog_v02_review.blend` 为通过 Blender MCP 导入游戏 GLB 后保存的双角色检查场景。运行中的 Blender 场景名为 `BlackDog_V02_Delivery`，其他已有场景保留。

## 毛发与材质

毛发为带蒙皮的双面 hair cards，使用 glTF 标准 `MASK` 透明裁切，不依赖 Blender 粒子、曲线毛发或专用毛发插件。基底和眼鼻为烘焙基色贴图，毛发用共享透明图和顶点色。

沿用角色色板；为 PBR 光照下的辨识度，v02 烘焙底毛调整为 `#211E1C`，白斑 `#E9DDC9`，暗眼 `#171D21`，虹膜 `#302820`，鼻头 `#171616`，眼部高光 `#FFF9E9`。这不是直接拿渲染截图像素当 HEX。

Godot 配套 `.glb.import` 与 `scripts/black_dog_import.gd` 必须一起保留：

- 开启毛发顶点色，关闭将顶点色再次按 sRGB 解码。
- 毛发使用带 mipmap 的 Linear 采样，并在 Godot 中改为 Alpha Depth Pre-Pass 软透明，避免硬裁切造成的细毛噪点或整片消失。
- 预览启用 4× MSAA。软透明有额外 overdraw 成本，远距离和大量同屏角色仍需按目标平台制作专用 LOD 或降低毛发密度。
- 关闭通用自动几何 LOD，避免简化器破坏细长毛片；角色不参与静态光照烘焙。

GLB 标准材质使用双面 Alpha Clip（阈值 0.35）和顶点色；Godot 配套导入脚本按实测切换为软透明深度预通道。其他引擎需按其透明采样实现选择对应毛发材质，不能假定跨引擎光照和透明效果完全相同。

## 骨骼与使用范围

骨骼命名与 v01 一致：躯干、头、下颌、四肢、耳朵、6 节尾骨。提供 FK 变形骨架，不含 IK 控制器。两年龄阶段骨长不同，不能直接交换 inverse bind matrices。

内含 `Idle`、`TailWag` 两个 30 fps / 2 秒动作。预览脚本会开启循环。没有行走、奔跑、口型、角色控制器或碰撞体；这是可直接导入和播放现有动画的游戏模型，不是完整宠物玩法系统。

本工程打开 `scenes/black_dog_3d_preview.tscn` 后按 F6。正式使用可把 GLB 拖进 `Node3D`；2D 场景需要 `SubViewport` 或预渲染帧动画，不能直接把 3D 模型当作 Sprite2D 贴图。

## 验证与复现

```text
blender --background --factory-startup --python scripts/build_black_dog_v02.py
python tests/validate_black_dog_glb.py
godot --headless --editor --import --quit
godot --headless --script res://tests/validate_black_dog_3d.gd --quit-after 120
godot --rendering-method gl_compatibility --script res://tests/capture_black_dog_preview.gd
```

生成脚本复用 `scripts/build_black_dog_3d.py` 的几何工具和检查函数，必须使用独立后台 Blender 进程；会清理该进程的活动场景。测试覆盖权重、UV、有限变形、GLB 内嵌纹理、材质透明模式、29 骨导入、动作播放和实际尾骨姿态变化。

同目录的 `*_beauty/front/side/back/pose_check.png` 为 Blender 渲染，`*_godot.png` 为 Godot 实录截图；两者光照不同，不承诺逐像素一致。`*_validation.json` 为对应测试结果。

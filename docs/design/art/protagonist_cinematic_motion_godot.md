# 主角电脑办公场景 · Godot 律动实现

## 场景入口

- 主场景：`scenes/cinematic_desk_demo.tscn`
- 场景控制：`scripts/cinematic_desk_demo.gd`
- 环境粒子：`scripts/cinematic_desk_ambient.gd`
- 局部形变：`shaders/cinematic_desk_motion.gdshader`
- 原始画面：`assets/art/daily/protagonist_cinematic_desk_v01.png`
- Godot 预览：`assets/art/daily/protagonist_cinematic_desk_godot_preview_v01.png`

## 律动层次

1. 角色呼吸：局部椭圆遮罩仅影响上身，产生约 1–2 像素的纵向呼吸形变。
2. 角色微动作：头部低频轻移，键盘手与鼠标手使用不同相位的小幅位移。
3. 窗帘与植物：窗边盆栽、书架垂叶和前景叶片使用不同遮罩、频率与相位摆动，避免整张背景平移。
4. 空气粒子：三组 `CPUParticles2D` 分别表现室内金色浮尘、窗前冷色微粒和低密度叶屑，使用运行时生成的柔光与叶形纹理，不依赖额外贴图。
5. 光线：两束半透明阳光缓慢呼吸，地板反光轻微移动。
6. 桌面文件：文件堆顶部与零散纸页分别起伏，并让文件底部阴影随高度轻微变化。
7. 电脑：显示器冷色辉光以低频脉冲照亮人物手部与桌面。
8. 相机：位置约 1–2 像素漂移，缩放幅度约 0.35%，形成不易察觉的镜头呼吸。

所有效果保持低幅度，避免影响 UI 阅读或让静态插画出现明显橡皮形变。粒子位置使用固定随机种子，方便录制、测试和复现。

## 操作

- `Space`：平滑开启或关闭全部律动效果。
- `Esc`：退出运行场景。

粒子会随律动强度同步调整透明度和播放速度；关闭效果时停止发射，重新开启时平滑恢复。

## 验证

- Godot 版本：4.7.1 stable，Compatibility 渲染器。
- 无头导入用于检查资源和脚本解析。
- 图形渲染运行 7 秒并成功导出 1280 × 720 预览截图。

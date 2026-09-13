# AGENTS.md

## 项目简介

- 游戏名称：律师模拟器（暂定）。
- 游戏类型：2D 模拟器游戏（目标平台待补充）。
- 技术栈：Godot 4.x + GDScript。
- 仓库地址：https://github.com/pytho-xiangda/lvshjmoniqi.git（GitHub 远端为 `origin`）。
- 设计文档：`docs/GDD.md` 是项目设计的权威文档，所有系统设计以它为准；设计变更时需同步更新。
- 跨任务共享上下文：设计产出统一放 `docs/design/`，各任务共用该目录与 git 仓库；关键产出在本文件登记路径。
- 美术基准：`assets/art/main_menu_concept.png`；统一美术、人物立绘与 UI 执行规范：`docs/design/art/art_direction.md`；生成提示词：`docs/design/art/generation_prompts.md`。后续美术默认沿用此风格。
- 庭审主要战斗场景与非写实卡牌风格探索：`docs/design/art/battle_cards.md`；对应图片放在 `assets/art/battle/` 与 `assets/art/cards/`。
- 已确认庭审方向为“超现实纸境＋纸境卡牌”；人物与动效规范：`docs/design/art/paper_battle_motion.md`；动态预览：`docs/design/art/paper_battle_preview.html`。
- 当前日常房间为固定正侧视横版场景：`assets/art/daily/daily_room_side_v04.png`；人物比例、12 帧行走与接入规范：`docs/design/art/daily_room_side_v04.md`；可交互预览：`docs/design/art/daily_room_side_preview.html`；24 fps 场景动画：`assets/videos/daily_room_side_walk_v04.mp4`。v01–v03 为历史草案。
- 庭审对手不限于律师，角色特征可外化为非写实躯体与周期招式；阴影法官与勾兑型「宴席客」规范：`docs/design/art/boss_banquet.md`。
- 庭审战斗 BGM：`docs/design/audio/court_bgm_16bits.md`；五首音频在 `assets/audio/bgm/court_16bits/`，试听页为 `docs/design/audio/court_bgm_preview.html`。
- 庭审舒缓版《纸页间的沉思》：`assets/audio/bgm/court_soft/06_quiet_deliberation.wav`；配方为 `docs/design/audio/court_bgm_soft.json`。
- 舒缓钢琴试作《草地上的云》：`docs/design/audio/meadow_piano.md`；WAV、MP3、MIDI 及乐谱在 `assets/audio/bgm/meadow_piano/`。
- 当前仓库尚未创建 `project.godot`，因此 Godot 导入与运行验证需待工程入口建立后执行。
- 主要版本以 `project.godot` 中 `config/features` 声明的 Godot 版本为准；如果与本文冲突，以 `project.godot` 为准并更新本文。

## 项目结构

按以下目录组织资源，新增内容时遵循已有结构：

- `scenes/`：场景文件（`.tscn`）
- `scripts/`：GDScript 脚本（`.gd`）
- `assets/`：美术、音频、字体等素材，可再分子目录
- `addons/`：Godot 插件（如测试框架 GUT）
- `tests/`：自动化测试脚本
- `project.godot`：项目配置，`project.godot` 与场景、脚本一样是代码，必须提交

## GDScript 编码规范

- 缩进使用 4 个空格，不用 Tab。
- 命名：变量和函数用 `snake_case`，类、场景、节点名用 `PascalCase`，常量用 `UPPER_SNAKE_CASE`。
- 新代码尽量写类型标注，例如 `var speed: float = 300.0`、`func move_to(target: Vector2) -> void`。
- 信号名用过去式，例如 `health_changed`、`game_over`。
- 节点引用优先用 `@onready`，可调参数优先用 `@export`，避免硬编码魔法数值。
- 注释解释"为什么"而不是"是什么"；不要给显而易见的代码加注释。
- 每个脚本职责单一：避免在 `_process()` 里堆砌所有逻辑，保持场景与脚本一一对应、职责清晰。
- 不要滥用全局状态；Autoload 只用于真正全局的服务（如音频、存档）。

## 素材与场景注意事项

- 新增素材后需要让 Godot 完成导入；`.godot/` 目录是缓存，永远不要提交。
- 场景文件优先使用文本格式（`.tscn`）以便 review 和合并。
- 不要提交导出的构建产物（如 `build/`、可执行文件、打包压缩包）。

## 验证

每次完成一处修改后，在提交前至少做一次验证：

1. 无头导入检查：`godot --headless --import`
2. 若有 GUT 测试：`godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests -gexit`
3. 如果项目已配置 CI，确保 CI 通过后再合并/推送。

## Git 与 GitHub 工作流（重要）

- 所有代码改动完成后，必须提交到 git 并推送到 GitHub 远端，不要只留在本地。
- 提交前先检查改动：`git status` 和 `git diff`，只提交与本次任务相关的文件。
- 提交信息使用 Conventional Commits 格式：`feat:`、`fix:`、`refactor:`、`docs:`、`test:`、`chore:`，例如 `feat: 添加玩家基础移动`。语言保持中文或英文一致。
- 一个逻辑改动对应一个提交，避免一次性提交大量无关改动。
- 禁止提交密钥、token、本地绝对路径配置、`.godot/` 缓存和构建产物。
- 推送命令：`git push origin <branch>`；在创建分支/提交/推送前先确认远端和分支状态。

## 沟通约定

- 与用户使用中文交流。
- 开始任务前先说明计划；任务完成后总结改动内容与验证结果。
- 若发现本文与实际项目不一致（例如 Godot 版本升级、目录调整），主动提醒并更新本文。

## 媒体生成工具（MiniMax）

游戏素材（图像/视频）的生成封装在 `scripts/minimax_gen.py`，供 Codex 快速调用。真实 API Key 放在项目根目录 `.env`（已 gitignore，绝不提交），可参照 `.env.example` 填写。

- 配置读取优先级：环境变量 > `.env` > 内置默认值；变量为 `MINIMAX_API_KEY`、`MINIMAX_BASE_URL`。
- ⚠️ 基址必须与你的 Key 来源一致：大陆版平台（platform.minimaxi.com）用 `https://api.minimaxi.com`，国际版平台（platform.minimax.io）用 `https://api.minimax.io`，两者 Key 不通用。本项目当前使用大陆版 `.com`（在 `.env` 中指定）。
- 图像用 `image-01`，视频用 `MiniMax-H3`（均为 `Bearer` 鉴权，无需 GroupId）。
- 输出目录约定：图像 → `assets/art/`，视频 → `assets/videos/`；用 `--out` 指定文件或目录。

调用示例：

```bash
# 文生图
python scripts/minimax_gen.py image --prompt "吉卜力水彩，律所窗外暖棕天空蓝" --out assets/art/scene.png

# 参考图生图（保持一致的人物形象）
python scripts/minimax_gen.py image --prompt "同一角色站在法院门口" --reference-image ref.png --out assets/art/

# 文生视频
python scripts/minimax_gen.py video --prompt "云朵缓缓飘过 15s, 16:9" --out assets/videos/sky.mp4

# 图生视频（首帧）
python scripts/minimax_gen.py video --prompt "让这张图动起来" --image first.png --out assets/videos/court.mp4

# 只打印请求体、不真正调用（用于校验/预览）
python scripts/minimax_gen.py video --prompt "test" --dry-run
```

常用参数：`--model`、`--resolution`、`--duration`、`--ratio`、`--aspect-ratio`、`--reference-image/--reference-video/--reference-audio`（视频参考，可多次）、`--poll-interval`、`--max-time`。各子命令可用 `--help` 查看。

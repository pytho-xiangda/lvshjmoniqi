# AGENTS.md

## 项目简介

- 游戏名称：律师模拟器（暂定）。
- 游戏类型：2D 模拟器游戏（目标平台待补充）。
- 技术栈：Godot 4.x + GDScript。
- 仓库地址：https://github.com/pytho-xiangda/lvshjmoniqi.git（GitHub 远端为 `origin`）。
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

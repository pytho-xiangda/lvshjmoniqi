# 纸境庭审战斗 BGM · 16bits 合成版

本组使用 [Matuyuhi/16bits-audio-mcp](https://github.com/Matuyuhi/16bits-audio-mcp) 在本机生成，不使用云端音乐 API、采样音色库或人声。风格是复古合成游戏音乐，与“超现实纸境”战斗场景搭配的第一组可试听素材。

## 文件与用途

试听入口：`docs/design/audio/court_bgm_preview.html`。

音频目录：`assets/audio/bgm/court_16bits/`。均为 44.1 kHz、16-bit PCM、单声道 WAV；整段循环，峰值统一为 −3 dBFS。

| 文件 | 名称 | 用途 | BPM／拍号 | 时长 |
| --- | --- | --- | --- | --- |
| 01_shadow_bench.wav | 阴影审判席 | 开庭压迫、回合思考 | 84／4/4 | 91.43 秒 |
| 02_evidence_clash.wav | 证据交锋 | 常规举证、连续攻防 | 118／4/4 | 81.36 秒 |
| 03_oily_banquet.wav | 觥筹暗涌 | 宴席客、勾兑蓄势 | 90／5/4 | 80.00 秒 |
| 04_rebuttal_surge.wav | 异议反击 | 破绽触发、高强度反击 | 136／4/4 | 84.71 秒 |
| 05_final_statement.wav | 最后陈述 | 终局辩论、宣判前 | 104／4/4 | 92.31 秒 |

第三首采用 5/4 错拍与小调和声体现宴席客的失衡感，不采用温暖的宴会华尔兹。周期招式仍由战斗逻辑触发；BGM 不决定回合计数。

## 生成与复现

- 主程序：上游 0.6.0，提交 `99a46c4057794ae4acc32105f95255a97f1e9277`。
- Zig：0.15.2，Windows x64，`ReleaseSafe` 构建。
- MCP SDK：上游锁定提交 `b6865d2cfb3626a18279ee5659a8df7a6d8a607d`。
- 主项目与 MCP SDK 的 LICENSE 均为 MIT；许可证副本存于本目录 `licenses/`。编译器、源码与可执行文件只保留在被忽略的 `.audio_runtime/`，不进入游戏仓库。
- Codex 已注册全局 stdio 服务 `16bits-audio`。它指向本机 `.audio_runtime/16bits-audio-mcp/zig-out/bin/16bits-audio-mcp.exe`；移动项目后需重新执行 `codex mcp add` 更新路径。
- 配方：`docs/design/audio/court_bgm_16bits.json`，包括音阶、和弦、节拍、随机种子、密度与效果链。
- 渲染脚本：`scripts/generate_court_bgm_16bits.py`，仅需 Python 标准库，通过真实 MCP `initialize`、`tools/list`、`tools/call` 完成生成。

```powershell
python scripts/generate_court_bgm_16bits.py --out .audio_runtime/reproduce
```

脚本默认拒绝覆盖已有素材；明确替换时使用 `--force`。每首启动独立 MCP 进程，避免上游全局打击乐噪声状态影响跨会话复现。服务器负责四轨作曲及效果处理，脚本最后仅修整循环接缝与峰值；不改变小节时长。

## 验证与接入边界

- MCP 握手成功、列出 10 个工具，五首均完成 `bgm_compose`、`wav_fx`、`wav_info` 调用。
- 五首均为非静音音频，无削波采样；首尾采样差为 0，时长与小节配方误差小于 2 毫秒。原始混响与音乐转折仍需结合战斗音效试听调整；采样连续不等于所有音乐切换都无感。
- 详细帧数、峰值、RMS、SHA-256 见音频目录中的 `audio_validation.json`。
- 五首独立重生成后 SHA-256 全部一致；浏览器验证五首均可解码，播放、单曲互斥、循环开关与窄屏布局正常。
- 上游算法测试 51/54 通过；另外 3 个 WAV 文件测试使用硬编码 `/tmp/` 路径，在 Windows 下失败。实际生成的五份 WAV 已通过独立读写、格式及幅度检查。
- 当前仓库尚无 `project.godot`，本机未找到 Godot 命令，因此无法执行 Godot 无头导入或游戏内播放验证。此次交付为音频素材和试听页，尚未绑定战斗状态机。
- 后续导入 Godot 时启用 WAV 的 Forward 循环，范围为完整文件；切换战斗强度可由游戏音频总线进行交叉淡化。建议先在试听页比较五首，再确定各阶段音乐音量。

早期 `court_bgm_prompts.json` 是云端方案草案；本次成品使用 `court_bgm_16bits.json`，两者音色与拍号不能混作同一版本。

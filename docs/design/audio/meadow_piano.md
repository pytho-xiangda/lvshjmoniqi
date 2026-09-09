# 草地上的云 · 舒缓钢琴试作

根据“像在云南草地上躺着看云”的意象创作。独奏钢琴，D 大调，轻柔分解和弦、宽音程与留白；中段旋律稍微抬高，末段逐渐放缓并自然收束。不含鼓、电子铺底、人声或环境音。

## 成品

目录：`assets/audio/bgm/meadow_piano/`。

- `07_clouds_over_meadow.wav`：约 98.14 秒，44.1 kHz、16-bit、立体声母版。
- `07_clouds_over_meadow.mp3`：192 kbps 试听版。
- `07_clouds_over_meadow.mid`：可编辑演奏事件；以 60 BPM 固定时间网格保存自由速度和细微时值变化，不能直接按网格小节理解乐句。
- `score.json`：实际 24 小节结构、约 61–65 BPM 的主要速度、尾声渐慢到 55 BPM，以及 154 个音符的时间和力度。
- `audio_validation.json`：音频及音色文件哈希、格式和幅度检查。

这是一首自然结束的试听小品，尚未制作无缝循环版或绑定战斗场景。原有庭审音频均保留。

## 音色与复现

此次使用 GeneralUser GS 的 `Grand Piano` 钢琴采样，由 TinySoundFont 本地渲染；不是前两组的基础波形音色，也不是真人现场演奏。右手力度约 42–55，左手更轻，踏板随和声换气，轻微早期反射提供空间。

生成脚本：`scripts/generate_meadow_piano.py`。依赖 `numpy`、`mido==1.3.3`、`tinysoundfont==0.3.7`，不调用网络或音频 API。

```powershell
python scripts/generate_meadow_piano.py --soundfont path/to/GeneralUser-GS.sf2 --out output/meadow-piano
```

脚本输出 WAV、MIDI、乐谱与检查数据；试听 MP3 可用 FFmpeg 编码：

```powershell
ffmpeg -n -i output/meadow-piano/07_clouds_over_meadow.wav -c:a libmp3lame -b:a 192k output/meadow-piano/07_clouds_over_meadow.mp3
```

[GeneralUser GS 官方仓库](https://github.com/mrbumpy409/GeneralUser-GS)及[官方许可证](https://github.com/mrbumpy409/GeneralUser-GS/blob/main/documentation/LICENSE.txt)：许可允许私人及商业音乐创作；作者也披露部分历史采样来源不能完全追溯。音色库本身不随本次游戏素材提交，不能将它标记为 MIT。TinySoundFont Python 绑定使用 MIT 许可。

## 验证

WAV 非静音，峰值约 −5 dBFS、RMS 约 −22.80 dBFS、无削波采样；MP3 完整解码通过。当前项目无 `project.godot`，未执行游戏内导入。此版主要供用户试听意境与钢琴音色。

# 横版日常房间 v06 · 行走原画提示词

工具：内置 imagegen 图片编辑。输入为 v03 的四张主角侧面行走参考图，输出为八阶段横向原画表。后处理脚本仅清除洋红色背景、统一比例与锚点并打包图集。

```text
Create a production-ready 2D game animation model sheet for the exact same young male protagonist shown in the reference images. Preserve his identity, side-profile face, wavy dark-brown hair, white rolled-sleeve shirt, charcoal straight trousers, brown leather shoes, body proportions, watercolor linework, paper grain, restrained warm-neutral palette and hand-painted animation style.

Deliver ONE clean sprite sheet containing exactly 8 equally sized full-body frames in a single horizontal row, all facing LEFT, with identical scale, head size, clothing design and foot ground line. Each frame must be a distinct sequential phase of one natural relaxed walk cycle suitable for a side-scrolling daily-life game:
1 left heel contact / right toe push-off,
2 recoil/down with left knee absorbing weight,
3 passing pose with right foot lifted under the hips and left foot flat,
4 high/up pose with right knee moving forward and left heel rising,
5 right heel contact / left toe push-off,
6 recoil/down with right knee absorbing weight,
7 passing pose with left foot lifted under the hips and right foot flat,
8 high/up pose with left knee moving forward and right heel rising.
Arms swing opposite the legs with relaxed elbows and open natural shoulders; pelvis and shoulders counter-rotate subtly; torso rises and falls gently; coat/shirt hems and hair have subtle secondary motion. The stride is comfortable and extended, never stiff. Feet show heel-to-toe roll and the planted foot reads firmly grounded. No duplicated poses, no sliding, no leaning backward, no exaggerated run.

Layout requirements: full character visible in every cell with generous transparent-looking empty margin, consistent ground baseline, no overlap between cells, no labels, no numbers, no grid lines, no UI, no scenery, no shadows. Use a flat solid chroma-magenta (#ff00ff) background across the whole sheet so it can be removed programmatically. Wide 4:1 sprite-sheet composition, high detail but clean readable silhouettes at game scale.
```

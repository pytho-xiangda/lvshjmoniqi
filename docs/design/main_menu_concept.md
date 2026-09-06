# 主界面效果图

- 文件：`assets/art/main_menu_concept.png`
- 生成方式：内置 imagegen。
- 状态：静态主菜单视觉概念，文字与背景合成，尚未接入 Godot 交互或动画。
- 依据：`docs/GDD.md` 第 10 节的暖色手绘水彩律所窗景。
- 人物为视觉示意，不锁定玩家性别和最终外观。
- 菜单：开始执业、继续旅程、游戏设置、离开游戏。无存档时继续旅程淡显。
- 后续接入需拆分无字背景与原生文本、按钮；新游戏从序章实习起点开始。

## 生成提示词

```text
Use case: ui-mockup, illustration-story.
Create a polished full-screen main menu concept image for a Chinese 2D narrative career simulation game titled “律师模拟器”. Landscape 16:9, 1920x1080-like composition, beautifully finished indie game screenshot, no device frame.
Art direction: original hand-painted watercolor animation background, delicate pencil contours, warm walnut browns, sky blue, cream paper, muted sage, late summer sunshine, gentle nostalgic hopeful mood with a hint of adult responsibility. Fine textured pigment and convincing architecture, no imitation of any specific existing film.
Composition: left 40% is quiet cream-colored wall/paper-lit negative space with elegantly typeset readable Chinese title and menus; right 60% is an atmospheric small Chinese law office beside a large open wood-framed window. A young graduate in white shirt, dark trousers, jacket draped over chair, seated three-quarter rear view at a wooden desk reading a case folder; appearance understated, no identifiable real person. On the desk stacked law books, folders tied with string, ceramic tea cup, brass desk lamp, small potted plant; graduation photo leans on book stack. Outside are leafy camphor trees, a distant modern Chinese city and billowing blue-white clouds. Sunlight creates rich long leaf shadows on wood, a few floating leaves beyond window. No judge gavel in office, no American flag, no western courtroom.
UI design: sophisticated restrained editorial title treatment in dark ink-brown Chinese serif. Top-left small letterspaced text “一纸委托，一段人生”. Large title arranged in two purposeful lines “律师” / “模拟器”, tiny English subtitle “THE MAKING OF A LAWYER”. Under title subtle thin brass rule and Chinese tagline “在法条与人情之间，写下你的答案。”
Below, a generous aligned vertical menu with four exact Chinese labels: “开始执业”, “继续旅程”, “游戏设置”, “离开游戏”. First item is selected, a muted deep forest green rectangular button with fine gold outline and a small cream right arrow; other three are understated dark-brown text on cream with generous spacing, “继续旅程” subtly lighter disabled appearance. Bottom-left small chapter teaser “序章 · 毕业季”. Bottom-right unobtrusive text “案件与人物均为虚构”.
Text must be clear, accurately spelled simplified Chinese, beautifully spaced, strong hierarchy. UI occupies left side without covering character. Background and menu form one cohesive game art image, not a website, no dashboard cards, no extra navigation, no watermark.
```


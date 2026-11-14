# SIZE MATTERZ（貪吃ㄐ）

斜俯視 3D 貪食蛇原型，手機優先。從別人尾巴後方 ±45° 撞進去，就能插入整條蛇。

## 試玩
- 線上：https://aquarius4224.github.io/sizematterz/
- 離線：下載 `standalone/貪吃ㄐ.html`，直接用瀏覽器開（three.js 已內嵌，不需網路）

## 檔案
- `index.html`：可直接上線的完整版（含手機 viewport 設定、three.js 內嵌），GitHub Pages 用這個
- `standalone/貪吃ㄐ.html`：同一份離線版
- `src/game.html`：遊戲原始碼（Claude Artifact 用的片段，沒有 head / viewport，不能直接當網頁上線）
- `title-src/`：開場標題素材
  - `art/SIZE_MATTERZ_layers.ora`：標題分層圖（19 層，可用 Krita / GIMP 開啟）
  - `art/gen_art.py`：把 ORA 圖層轉成內嵌的 `TITLE_ART`
  - `art/title4.js`：標題動畫
  - `glyphs.py`、`bl_build.py`、`comp.py`：先前的 Blender 充氣字實驗（已暫停）
- `previews/`：各版本截圖

## 音樂

- 選單／開場：“Bit Shift” Kevin MacLeod (incompetech.com)，授權 CC BY 4.0：https://creativecommons.org/licenses/by/4.0/

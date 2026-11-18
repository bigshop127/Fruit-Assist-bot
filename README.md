# 水果 2048 輔助器 · 使用說明 / Fruit 2048 Assistant · User Guide

[中文](#中文) · [English](#english)

### ⬇️ 下載 / Download

| 版本 / Version | 下載 / Download |
|---|---|
| 🇹🇼 中文版（介面全中文） | [**Fruit2048Assistant_Chinese.zip**](https://github.com/bigshop127/Fruit-Assist-bot/releases/latest/download/Fruit2048Assistant_Chinese.zip) |
| 🇬🇧 English version (English interface) | [**Fruit2048Assistant_English.zip**](https://github.com/bigshop127/Fruit-Assist-bot/releases/latest/download/Fruit2048Assistant_English.zip) |

兩個版本功能完全一樣，只差介面語言。所有版本列表在 [Releases](https://github.com/bigshop127/Fruit-Assist-bot/releases)。<br>
Both versions are identical apart from the interface language. All versions: [Releases](https://github.com/bigshop127/Fruit-Assist-bot/releases).

---

## 中文

### 這是什麼
一個 Windows 小程式：盯著電腦螢幕上的水果 2048 盤面，自動認出每一格是幾號水果，
算出最好的滑動方向。可以只顯示建議（大箭頭，你自己滑），也可以讓它**自己玩**。

### ⚠️ 一定要在電腦上用模擬器玩
輔助器是靠**截取電腦螢幕畫面**來認盤面的，所以遊戲必須開在**同一台電腦**的
Android 模擬器裡（例如 BlueStacks、雷電模擬器 LDPlayer、MuMu 模擬器），
模擬器視窗要**看得到、不能被擋住**。

**在手機上直接玩的話，輔助器看不到畫面，不會同步。**

### 需要什麼
- Windows 10 / 11 電腦
- 一個 Android 模擬器，裡面裝好水果 2048 遊戲
- 輔助器本身：
  - **免安裝版（推薦）**：到上面的「下載」選 **中文版** 或 **English version**，不用另外裝任何東西
  - 原始碼版：要先裝 [Python 3.9 以上](https://www.python.org/downloads/)
    （安裝時勾選「Add Python to PATH」），再雙擊 `啟動輔助器.bat`（原始碼：本頁上方綠色「Code」→「Download ZIP」），第一次會自動裝套件

### 安裝
1. 把下載的 zip **整個解壓縮**到一個資料夾（例如桌面或 `D:\水果2048`）。
   不要直接在 zip 裡面點開，也不要放在 `C:\Program Files`（程式要在同一個資料夾存設定）。
2. 雙擊 `水果2048輔助器.exe`。
3. 如果跳出藍色的「Windows 已保護您的電腦」：按 **「其他資訊」→「仍要執行」**。
   （這個程式沒有花錢買數位簽章，所以 Windows 不認識它；防毒軟體偶爾也會誤報。）

`templates.json`（已經學好的水果外觀）要跟 exe 放在**同一個資料夾**。

### 第一次使用（只要做一次）
先開模擬器、進到遊戲盤面，再操作輔助器：

**① 校準盤面**
1. 按「① 校準盤面」，整個畫面會變暗。
2. 沿著**左上角那一格**的格子邊框拖一個框。
3. 再依序點 **右上 → 右下 → 左下** 三格的**中心**。點錯按 `Backspace` 退一步。
4. 確認視窗裡的紫框有套住每顆水果就按「確定」。
   有點偏可以用方向鍵微調（`Ctrl`+方向鍵 一次 10px、`Shift`+方向鍵 改大小）。

**② 標記水果**
- 如果按完「確定」顯示「有 N 格對不上之前學過的樣板」（你的模擬器大小跟原本的不一樣），
  就按「② 標記水果」：每一格下面填水果上的號碼，**空格填 0**，按「存檔並開始」。
- 只要標一次，之後會記住。遊戲裡新合成出來的水果它通常會自己看號碼學起來。
- 遊戲換了活動主題（背景、格子花紋變了）時，可能要再標一次。

| 號碼 | 水果 | 號碼 | 水果 | 號碼 | 水果 |
|---|---|---|---|---|---|
| 1 | 蘋果 | 5 | 葡萄 | 9 | 鳳梨 |
| 2 | 橘子 | 6 | 檸檬 | 10 | 藍莓 |
| 3 | 香蕉 | 7 | 桃子 | 11 | 櫻桃 |
| 4 | 西瓜 | 8 | 芒果 | 12 | 奇異果 |

### 平常怎麼玩
- **只看提示**：開著就好，大箭頭就是建議的方向，你自己在模擬器裡滑。
- **讓它自己玩**：按綠色「▶ 開始自動玩」，它會用滑鼠在模擬器上滑動。
  - **要停：按 `F8`**（不用切回輔助器視窗），或按紅色「■ 停止自動玩」。
  - 自動玩的時候會借用你的滑鼠，這段時間別同時用電腦做別的事。

### 注意事項
- 輔助器視窗**不要蓋在盤面上**，把它拖到模擬器旁邊。
- 模擬器視窗**開大一點**比較好認（盤面太小時，水果上的號碼小到讀不出來，新水果就得手動標）。
- 想換介面語言：在 exe 旁邊的 `config.json` 加一行 `"language": "en"`（或 `"zh"`），重開程式。
- 模擬器視窗可以**移動**（會自動跟上），但**改變視窗大小**後要重新「① 校準盤面」。
- 讀不到盤面時（例如被其他視窗擋住），按「重新吸附」或重新校準。
- 每次打開程式，自動玩都是關著的，不會一開就搶滑鼠。

---

## English

### What it is
A small Windows app that watches the Fruit 2048 board on your screen, recognises which fruit is
in each cell, and works out the best move. It can just show a hint (a big arrow — you swipe
yourself) or **play by itself**.

### ⚠️ You must play on a PC, inside an Android emulator
The assistant reads the board by **capturing your PC screen**, so the game has to run in an
Android emulator **on the same computer** (e.g. BlueStacks, LDPlayer, MuMu Player), and the
emulator window must be **visible and not covered**.

**If you play on your phone, the assistant cannot see the game and will not sync.**

### Requirements
- A Windows 10 / 11 PC
- An Android emulator with the Fruit 2048 game installed
- The assistant itself:
  - **Portable version (recommended)**: pick **English version** (or 中文版) under "Download" above — nothing else to install
  - Source version: install [Python 3.9+](https://www.python.org/downloads/) first (tick
    "Add Python to PATH"), then double-click `啟動輔助器.bat` (source: green "Code" button → "Download ZIP" at the top of this page); packages install automatically on first run

### Install
1. **Extract the whole downloaded zip** into a folder (e.g. Desktop or `D:\Fruit2048`).
   Don't run it from inside the zip, and don't put it under `C:\Program Files` — the app saves
   its settings in its own folder.
2. Double-click `Fruit2048Assistant.exe` (Chinese version: `水果2048輔助器.exe`).
3. If a blue "Windows protected your PC" box appears, click **"More info" → "Run anyway"**.
   (The app isn't code-signed, so Windows doesn't recognise it; antivirus may occasionally flag it too.)

Keep `templates.json` (the already-learned fruit images) **in the same folder** as the exe.

### First run (one time only)
Open the emulator and get to the game board first, then:

**① Calibrate the board**
1. Click it — the screen dims.
2. Drag a box around the **top-left cell** of the board.
3. Then click the **centre** of the **top-right → bottom-right → bottom-left** cells, in that order.
   `Backspace` undoes a click.
4. If the purple boxes in the preview sit on each fruit, click OK. Nudge with the arrow
   keys if needed (`Ctrl`+arrow = 10 px, `Shift`+arrow = resize).

**② Label the fruits**
- If after OK it says some cells don't match the learned templates (your emulator size differs),
  click `② Label fruits`, type the number shown on each fruit under its thumbnail, **0 for empty cells**,
  then click `Save & start`.
- You only do this once. New fruits that appear later are usually learned automatically from the number printed on them.
- When the game switches to a new event theme (different background / tile pattern) you may need to label once more.

Fruit numbers: 1 apple · 2 orange · 3 banana · 4 watermelon · 5 grape · 6 lemon ·
7 peach · 8 mango · 9 pineapple · 10 blueberry · 11 cherry · 12 kiwi

### Playing
- **Hints only**: just leave it open — the big arrow is the suggested direction; swipe in the emulator yourself.
- **Auto-play**: click the green `▶ Start auto-play` button and it will swipe in the emulator with your mouse.
  - **To stop: press `F8`** (works without switching windows), or click the red `■ Stop auto-play`.
  - Auto-play borrows your mouse — don't use the PC for anything else meanwhile.

### Tips
- **Don't let the assistant window cover the board** — put it beside the emulator.
- You can **move** the emulator window (the app follows it), but after **resizing** it you must calibrate again.
- If the board can't be read (e.g. something is covering it), click `Re-snap` or recalibrate.
- A **bigger emulator window** reads better (on a tiny board the numbers on the fruits are too small to read, so new fruits must be labelled by hand).
- To switch the interface language, add `"language": "zh"` (or `"en"`) to `config.json` next to the exe and restart.
- Auto-play is always off when the app starts, so it never grabs your mouse unexpectedly.

---

<sub>開發用技術文件見 [`DEVELOPMENT.md`](DEVELOPMENT.md)。<br>
Developer docs (Chinese): [`DEVELOPMENT.md`](DEVELOPMENT.md).</sub>

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
一個 Windows 小程式：盯著水果 2048 的盤面，自動認出每一格是幾號水果，算出最好的滑動方向。
可以只顯示建議（大箭頭，你自己滑），也可以讓它**自己玩**——甚至在背景自己玩，你同時用電腦做別的事、打別的遊戲。

**功能一覽**
- 即時建議方向（expectimax 搜尋）
- 自動玩，`F8` 隨時停止
- **背景模式**：透過模擬器的 adb 操作，不搶滑鼠；模擬器被其他視窗（例如全螢幕遊戲）蓋住也照跑
- 精簡視窗，`F9` 一鍵藏起來／叫回來
- 遊戲跳彈窗等暫時狀況打斷時，畫面恢復後**自己接回去**繼續玩
- **魚符計算**：現在盤面＋手上魚符，理論上最高能合到幾號、下一階還差幾個魚符

### ⚠️ 遊戲要開在電腦的 Android 模擬器裡
遊戲必須開在**同一台電腦**的 Android 模擬器（例如 BlueStacks、雷電模擬器 LDPlayer、MuMu 模擬器）。
**在手機上直接玩的話，輔助器看不到畫面。**

### 需要什麼
- Windows 10 / 11 電腦
- 一個 Android 模擬器，裡面裝好遊戲
- 輔助器本身：
  - **免安裝版（推薦）**：到上面「下載」選 **中文版** 或 **English version**，不用另外裝任何東西
  - 原始碼版：先裝 [Python 3.9 以上](https://www.python.org/downloads/)（安裝時勾選「Add Python to PATH」），
    再雙擊 `啟動輔助器.bat`（原始碼：本頁上方綠色「Code」→「Download ZIP」），第一次會自動裝套件

### 安裝
1. 把下載的 zip **整個解壓縮**到一個資料夾（例如桌面或 `D:\水果2048`）。
   不要直接在 zip 裡面點開，也不要放在 `C:\Program Files`（程式要在同一個資料夾存設定）。
2. 雙擊 `水果2048輔助器.exe`。
3. 如果跳出藍色的「Windows 已保護您的電腦」：按 **「其他資訊」→「仍要執行」**。
   （這個程式沒有花錢買數位簽章，所以 Windows 不認識它；防毒軟體偶爾也會誤報。）

`templates.json`（已經學好的水果外觀）要跟 exe 放在**同一個資料夾**。

### 視窗長什麼樣
平常是一個小視窗：大箭頭＋建議方向，下面一排按鈕：

| 按鈕 | 做什麼 |
|---|---|
| ▶ 開始自動玩 | 讓它自己玩；再按一次停止 |
| 暫停 | 暫停讀畫面（也會停掉自動玩） |
| 魚符 | 展開／收起魚符計算 |
| 詳細 | 展開／收起小盤面、四方向評分，以及「① 校準盤面」「② 標記水果」「重新吸附」「⚙ 設定」 |
| 隱藏 F9 | 把視窗藏起來（程式照跑），按 `F9` 叫回來 |

還沒校準時「詳細」會自動展開。

### 第一次使用（只要做一次）
先開模擬器、進到遊戲盤面，再操作輔助器：

**① 校準盤面**
1. 按「① 校準盤面」，整個畫面會變暗。
2. 沿著**左上角那一格**的格子邊框拖一個框。
3. 再依序點 **右上 → 右下 → 左下** 三格的**中心**。點錯按 `Backspace` 退一步。
4. 確認視窗裡的紫框有套住每顆水果就按「確定」。
   有點偏可以用方向鍵微調（`Ctrl`+方向鍵 一次 10px、`Shift`+方向鍵 改大小）。

**② 標記水果**
- 如果按完「確定」顯示「有 N 格對不上之前學過的樣板」，就按「② 標記水果」：
  每一格下面填水果上的號碼，**空格填 0**，按「存檔並開始」。
- 只要標一次，之後會記住。新合成出來的水果它通常會自己看號碼學起來。
- 遊戲換了活動主題（背景、格子花紋變了）時，可能要再標一次。

| 號碼 | 水果 | 號碼 | 水果 | 號碼 | 水果 |
|---|---|---|---|---|---|
| 1 | 蘋果 | 5 | 葡萄 | 9 | 鳳梨 |
| 2 | 橘子 | 6 | 檸檬 | 10 | 藍莓 |
| 3 | 香蕉 | 7 | 桃子 | 11 | 櫻桃 |
| 4 | 西瓜 | 8 | 芒果 | 12 | 奇異果 |

### 平常怎麼玩
- **只看提示**：開著就好，大箭頭就是建議的方向，你自己在模擬器裡滑。
- **讓它自己玩**：按綠色「▶ 開始自動玩」。
  - **要停：按 `F8`**（不用切回輔助器視窗），或按紅色「■ 停止自動玩」。
  - 預設是「滑鼠滑動」：會借用你的滑鼠，這段時間別同時用電腦做別的事。想邊跑邊做別的事，請改用下面的**背景模式**。
- **藏起來**：按「隱藏 F9」或直接按 `F9`，視窗整個消失、程式照跑；再按一次 `F9` 叫回來。快捷鍵可以在 ⚙ 換。
- **被打斷會自己接回去**：遊戲跳彈窗、合成動畫太久、模擬器一時沒反應而讓自動玩停下時，10 分鐘內畫面恢復正常就自己繼續。
  需要你手動點掉的彈窗（例如領獎勵）它沒辦法幫你點。遊戲結束、按 `F8`、按暫停則不會自己接。
  每次停下的原因記在 exe 旁的 `autoplay_log.txt`，視窗上也會顯示「幾點幾分停止：原因」。

### 背景模式（不搶滑鼠，可以同時打別的遊戲）
輔助器直接透過模擬器的 adb 讀畫面、送滑動，完全不碰你的滑鼠鍵盤，模擬器被別的視窗蓋住也沒關係。

1. **在模擬器打開 ADB**
   - BlueStacks：設定 → 進階 → 打開「Android 偵錯（ADB）」，記下下面顯示的位址（例如 `127.0.0.1:5555`；多開的第二個實例常是 `127.0.0.1:5565`）。改完重開模擬器。
   - 雷電、MuMu 也有類似的「ADB 偵錯」選項。
2. **到輔助器的 ⚙ 設定**（在「詳細」裡）
   - 「自動操控」區的「操控方式」選「背景滑動（模擬器 adb，不搶滑鼠）」，「模擬器 adb 位址」填剛剛的位址。
   - 「畫面來源」區的「來源」選「adb（手機或模擬器，可完全背景）」，「adb 序號」填同一個位址。
   - 按「套用」。
3. **重新「① 校準盤面」**：會跳出一張模擬器截圖，對著截圖框一樣的兩步。對不上就再「② 標記水果」一次。
4. 按「▶ 開始自動玩」，再按 `F9` 藏起視窗，就可以去做別的事了。模擬器要一直開著（被蓋住、放背後都沒關係）。

小提醒：
- 不用另外裝 adb——輔助器會自動找 BlueStacks／雷電／MuMu 附的 adb（電腦上有 Android SDK Platform-Tools 的話優先用它）。
- **多開模擬器（例如 BlueStacks「1」「2」輪流玩）不用改設定**：填的那台沒開時，會自動改用開著的那台；兩台都開著時，會用畫面上真的有水果盤面的那一台。兩台解析度不同也沒關係，校準範圍會照比例換算。
- 背景模式每看一次畫面約 0.25 秒，每一步比一般模式稍慢。
- 也可以只把「操控方式」改成背景滑動、畫面來源維持螢幕擷取：一樣不搶滑鼠、每步比較快，但模擬器盤面要露在螢幕上不能被擋住。
- 同時打別的遊戲覺得掉幀，可以在 ⚙ 把「思考時間」調低（例如 0.15）。

### 魚符計算
按「魚符」，填上遊戲裡的魚符數，會用目前讀到的盤面算出：
- 盤面相當於幾顆 1 號水果、加上魚符一共多少
- **理論上最高能合到幾號**（超過 12 號就用「12 號 ×幾顆」表示）
- 下一階、下下階各要幾個魚符、還差多少

換算方式：1 個魚符＝長出 1 顆 1 號；兩個 1 合一個 2、四個 1 合一個 3……n 號＝2^(n−1) 顆 1 號。
這是每一顆都完美合進去的上限，實際玩會低一點。

### 注意事項
- 一般模式（螢幕擷取）時，輔助器視窗**不要蓋在盤面上**，把它拖到模擬器旁邊。
- 模擬器視窗**開大一點**比較好認（盤面太小時，水果上的號碼小到讀不出來，新水果就得手動標）。
- 想換介面語言：在 exe 旁邊的 `config.json` 加一行 `"language": "en"`（或 `"zh"`），重開程式。
- 模擬器視窗可以**移動**（會自動跟上），但**改變視窗大小**後要重新「① 校準盤面」。
- 讀不到盤面時（例如被其他視窗擋住），按「重新吸附」或重新校準。
- 每次打開程式，自動玩都是關著的，不會一開就自己動。

---

## English

### What it is
A small Windows app that watches the Fruit 2048 board, recognises which fruit is in each cell, and
works out the best move. It can just show a hint (a big arrow — you swipe yourself) or **play by itself** —
even in the background while you use the PC for something else, including another game.

**Features**
- Live move suggestions (expectimax search)
- Auto-play, stop any time with `F8`
- **Background mode**: works through the emulator's adb, never touches your mouse, and keeps running even when the emulator is covered (e.g. by a full-screen game)
- Compact window; `F9` hides / shows it
- Resumes by itself after a game popup or similar briefly interrupts auto-play
- **Fish token calculator**: the highest fruit the current board plus your tokens can theoretically reach, and how many tokens the next step needs

### ⚠️ The game must run in an Android emulator on your PC
Run the game in an Android emulator **on the same computer** (e.g. BlueStacks, LDPlayer, MuMu Player).
**If you play on your phone, the assistant cannot see the game.**

### Requirements
- A Windows 10 / 11 PC
- An Android emulator with the game installed
- The assistant itself:
  - **Portable version (recommended)**: pick **English version** (or 中文版) under "Download" above — nothing else to install
  - Source version: install [Python 3.9+](https://www.python.org/downloads/) first (tick "Add Python to PATH"),
    then double-click `啟動輔助器.bat` (source: green "Code" button → "Download ZIP" at the top of this page); packages install automatically on first run

### Install
1. **Extract the whole downloaded zip** into a folder (e.g. Desktop or `D:\Fruit2048`).
   Don't run it from inside the zip, and don't put it under `C:\Program Files` — the app saves its settings in its own folder.
2. Double-click `Fruit2048Assistant.exe` (Chinese version: `水果2048輔助器.exe`).
3. If a blue "Windows protected your PC" box appears, click **"More info" → "Run anyway"**.
   (The app isn't code-signed, so Windows doesn't recognise it; antivirus may occasionally flag it too.)

Keep `templates.json` (the already-learned fruit images) **in the same folder** as the exe.

### The window
Normally it's a small window: a big arrow with the suggested direction, and one row of buttons:

| Button | What it does |
|---|---|
| ▶ Start auto-play | Let it play by itself; click again to stop |
| Pause | Stop reading the board (also stops auto-play) |
| Fish | Show / hide the fish token calculator |
| Details | Show / hide the mini board, move scores, and `① Calibrate board`, `② Label fruits`, `Re-snap`, `⚙ Settings` |
| Hide F9 | Hide the window (it keeps working); press `F9` to bring it back |

Details open by themselves until you've calibrated.

### First run (one time only)
Open the emulator and get to the game board first, then:

**① Calibrate the board**
1. Click it — the screen dims.
2. Drag a box around the **top-left cell** of the board.
3. Then click the **centre** of the **top-right → bottom-right → bottom-left** cells, in that order. `Backspace` undoes a click.
4. If the purple boxes in the preview sit on each fruit, click OK. Nudge with the arrow keys if needed
   (`Ctrl`+arrow = 10 px, `Shift`+arrow = resize).

**② Label the fruits**
- If after OK it says some cells don't match the learned templates, click `② Label fruits`, type the number
  shown on each fruit under its thumbnail, **0 for empty cells**, then click `Save & start`.
- You only do this once. New fruits that appear later are usually learned automatically from the number printed on them.
- When the game switches to a new event theme (different background / tile pattern) you may need to label once more.

Fruit numbers: 1 apple · 2 orange · 3 banana · 4 watermelon · 5 grape · 6 lemon ·
7 peach · 8 mango · 9 pineapple · 10 blueberry · 11 cherry · 12 kiwi

### Playing
- **Hints only**: just leave it open — the big arrow is the suggested direction; swipe in the emulator yourself.
- **Auto-play**: click the green `▶ Start auto-play`.
  - **To stop: press `F8`** (works without switching windows), or click the red `■ Stop auto-play`.
  - The default "mouse swipe" borrows your mouse, so don't use the PC meanwhile. To keep using the PC, use **Background mode** below.
- **Hide it**: click `Hide F9` or press `F9` — the window disappears but keeps working; press `F9` again to bring it back. The key can be changed in ⚙.
- **Resumes by itself**: if a game popup, a long merge animation or a brief emulator hiccup stops auto-play, it carries on
  once the board is readable again (within 10 minutes). It can't click away popups that need a tap (e.g. claiming a reward).
  Game over, `F8` and Pause are never resumed automatically. Every stop is logged to `autoplay_log.txt` next to the exe,
  and the window shows when and why it last stopped.

### Background mode (mouse stays free — you can even play another game)
The assistant reads the screen and swipes through the emulator's adb, never touching your mouse or keyboard,
and it doesn't matter if the emulator is covered by other windows.

1. **Enable ADB in the emulator**
   - BlueStacks: Settings → Advanced → turn on "Android Debug Bridge (ADB)" and note the address shown
     (e.g. `127.0.0.1:5555`; a second instance is often `127.0.0.1:5565`). Restart the emulator.
   - LDPlayer and MuMu have a similar "ADB debugging" option.
2. **In the assistant's ⚙ Settings** (under Details)
   - Auto-play section → `Input method`: `Background swipe (emulator adb…)`; `Emulator adb address`: the address above.
   - Screen source section → `Source`: `adb (phone or emulator…)`; `adb serial`: the same address.
   - Click `Apply`.
3. **Calibrate again (①)** — you'll mark the board on an emulator screenshot, same two steps. Label (②) again if cells don't match.
4. Click `▶ Start auto-play`, press `F9` to hide the window, and go do something else. Keep the emulator running (covered or in the background is fine).

Notes:
- No separate adb install needed — the assistant finds the adb bundled with BlueStacks / LDPlayer / MuMu
  (Android SDK Platform-Tools is preferred if installed).
- **Multiple emulator instances (e.g. BlueStacks "1" and "2") need no settings changes**: if the address you entered isn't running, it uses the one that is; if both are running, it uses the one actually showing the fruit board. Different resolutions are fine — the calibration is scaled automatically.
- In background mode each screen read takes about 0.25 s, so every move is a little slower.
- You can also switch only the input method to background swipe and keep screen capture: still mouse-free and faster per move,
  but the emulator's board must stay visible on screen.
- If another game drops frames meanwhile, lower `Thinking time` in ⚙ (e.g. 0.15).

### Fish token calculator
Click `Fish`, type how many tokens you have, and it uses the board it's currently reading to show:
- what the board is worth in #1 fruits, and the total with your tokens
- **the highest fruit you can theoretically reach** (beyond #12 it shows "#12 ×N")
- how many tokens the next couple of steps need and how many you're short

How it counts: 1 token = one new #1 fruit; two #1 make a #2, four make a #3 … a #n is worth 2^(n−1) #1 fruits.
This is a perfect-merge upper bound — real play ends a little lower.

### Tips
- In the normal (screen capture) mode, **don't let the assistant window cover the board** — put it beside the emulator.
- You can **move** the emulator window (the app follows it), but after **resizing** it you must calibrate again.
- If the board can't be read (e.g. something is covering it), click `Re-snap` or recalibrate.
- A **bigger emulator window** reads better (on a tiny board the numbers on the fruits are too small to read, so new fruits must be labelled by hand).
- To switch the interface language, add `"language": "zh"` (or `"en"`) to `config.json` next to the exe and restart.
- Auto-play is always off when the app starts, so it never starts moving by itself.

---

<sub>開發用技術文件見 [`DEVELOPMENT.md`](DEVELOPMENT.md)。<br>
Developer docs (Chinese): [`DEVELOPMENT.md`](DEVELOPMENT.md).</sub>

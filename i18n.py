"""介面語言（中文 / English）。

用法：`tr("中文原文")`，有變數就用具名佔位 `tr("已走 {n} 步", n=played)`。
中文版直接照原文 format；英文版用原文當 key 去查 `EN` 對照表。對照表漏了的
字串會退回中文而不是當掉 —— `test_i18n.py` 會掃過所有 `tr("...")` 確保沒漏。

語言怎麼決定（先找到的算數）：
  1. 環境變數 FRUIT2048_LANG=zh / en（開發測試用）
  2. config.json 裡的 "language"（使用者想換語言可以手動改）
  3. 打包時寫進 exe 的預設語言（`_build_lang.py`，由 tools/build_exe.ps1 產生）
  4. 都沒有就中文
語言在 import 這支模組的當下就決定，執行中不切換（模組層級的常數也會用到 tr）。
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict

SUPPORTED = ("zh", "en")


def _app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _detect() -> str:
    env = os.environ.get("FRUIT2048_LANG", "").strip().lower()
    if env in SUPPORTED:
        return env
    try:
        with open(os.path.join(_app_dir(), "config.json"), "r", encoding="utf-8") as f:
            lang = str(json.load(f).get("language", "")).strip().lower()
        if lang in SUPPORTED:
            return lang
    except (OSError, ValueError, AttributeError):
        pass
    try:
        from _build_lang import LANG as built  # type: ignore
        if built in SUPPORTED:
            return built
    except ImportError:
        pass
    return "zh"


LANG = _detect()


def tr(text: str, **kw) -> str:
    if LANG == "en":
        text = EN.get(text, text)
    return text.format(**kw) if kw else text


# 中文原文 → English。key 必須跟程式裡 tr() 的字串一字不差。
EN: Dict[str, str] = {
    # ---- 主視窗
    "水果 2048 輔助器": "Fruit 2048 Assistant",
    "等待中": "Waiting",
    "四個方向評分": "Move scores",
    "▶ 開始自動玩": "▶ Start auto-play",
    "■ 停止自動玩": "■ Stop auto-play",
    "① 校準盤面": "① Calibrate board",
    "② 標記水果": "② Label fruits",
    "重新吸附": "Re-snap",
    "暫停": "Pause",
    "繼續": "Resume",
    "繼續偵測": "Resume detection",
    "已暫停（畫面不會再更新）": "Paused (the board is no longer being read)",
    "已走 {n} 步 · {key} 停止 · {hide} 隱藏／叫回": "{n} moves · {key} stop · {hide} hide/show",
    "已走 {n} 步": "{n} moves",
    "{hide} 隱藏／叫回視窗": "{hide} hides / shows this window",
    "魚符": "Fish",
    "詳細": "Details",
    "隱藏 {key}": "Hide {key}",
    "手上魚符": "Fish tokens",
    "（1 魚符＝1 顆 1 號）": "(1 token = one #1 fruit)",
    "魚符請填整數": "Enter a whole number of tokens",
    "還沒讀到盤面": "No board read yet",
    "盤面＝{board:,} 顆 1 號，加魚符共 {total:,}": "Board = {board:,} × #1; with tokens {total:,}",
    "{lv} 號": "#{lv}",
    "理論最高：{best}（多出 {left:,}）": "Theoretical max: {best} ({left:,} left over)",
    "  {name}：要 {need:,} 魚符，還差 {short:,}": "  {name}: needs {need:,} tokens, {short:,} short",
    "  {name}：要 {need:,} 魚符 ✓": "  {name}: needs {need:,} tokens ✓",
    "理論值：假設每顆都完美合進去，實際會低一點": "Theoretical: assumes every fruit merges perfectly",
    "隱藏視窗鍵": "Hide-window key",
    "按一下藏起來、再按一下叫回來": "Press once to hide, again to show",
    "「隱藏視窗鍵」不能跟「緊急停止鍵」用同一個鍵": "The hide key can't be the same as the emergency-stop key",
    "往 {dir} 滑": "Swipe {dir}",
    "上": "UP", "下": "DOWN", "左": "LEFT", "右": "RIGHT",
    "鍵盤 {key}": "Keyboard {key}",
    "自動執行中…": "Auto-playing…",
    "不能動": "blocked",
    "最佳": "best",
    "深度 {depth}　{nodes:,} nodes　{ms:.0f} ms　樣板 {n} 張　擷取 {backend}":
        "depth {depth}  {nodes:,} nodes  {ms:.0f} ms  {n} templates  capture {backend}",
    "遊戲結束": "Game over",
    "畫面變動中…": "Board is changing…",
    "尚未校準": "Not calibrated",
    "需要標記": "Needs labels",
    "校準跑掉了": "Calibration drifted",
    "已停止": "Stopped",
    "出錯了": "Error",

    # ---- 狀態訊息
    "還沒校準。按下方的「① 校準盤面」框出遊戲的 4x4 區域。":
        "Not calibrated yet. Click \"① Calibrate board\" below and mark the game's 4x4 grid.",
    "找不到視窗「{title}」——可能被關掉或縮到最小了。還原視窗就會自動接回去繼續玩。":
        "Can't find the window \"{title}\" — it may be closed or minimised. "
        "Restore it and the assistant will pick up again automatically.",
    "偵測到 {key}，自動操控已停止。": "{key} pressed — auto-play stopped.",
    "抓不到畫面：{e}": "Couldn't capture the screen: {e}",
    "動畫播放中…": "Animation playing…",
    "樣板庫是空的。按「② 標記水果」教它每一格是幾號。":
        "No fruits learned yet. Click \"② Label fruits\" and tell it the number in each cell.",
    " 自動操控先停著，處理好會自己接回去。": " Auto-play is paused and will resume once this is fixed.",
    "{n} 格認不得 —— 多半是模擬器視窗移動過。按「重新吸附」試著自動修正。":
        "{n} cells not recognised — the emulator window probably moved. "
        "Click \"Re-snap\" to try to fix it automatically.",
    "有 {n} 格沒見過（大概是升級出新水果了）。按「② 標記水果」教它。":
        "{n} cell(s) not seen before (probably a new fruit). Click \"② Label fruits\" to teach it.",
    "四個方向都動不了 —— 這局結束了。": "No move is possible in any direction — game over.",
    "、": ", ",
    "看格子上的數字認出 {names} 號水果，已經記起來了":
        "Recognised fruit #{names} from the number on the tile and learned it",
    "連續滑了 {n} 次盤面都沒變化，已自動停止。請確認模擬器視窗在最上層、而且沒有被這個輔助器的視窗蓋住。":
        "Swiped {n} times with no change on the board, so auto-play stopped. Make sure the emulator "
        "window is on top and not covered by this assistant's window.",
    "送出操作失敗：{e}": "Failed to send the move: {e}",
    "內部錯誤：{e}": "Internal error: {e}",

    # ---- 校準（螢幕遮罩 / 手機截圖）
    "右上": "top-right", "右下": "bottom-right", "左下": "bottom-left", "左上": "top-left",
    "第 1 步 / 共 2 步　框出「左上角那一格」": "Step 1 of 2 — drag a box around the TOP-LEFT cell",
    "沿著左上角那一顆水果的格子邊框拖曳。這一步是用來量出一格有多大。　　Esc 取消":
        "Drag along the border of the top-left fruit's cell. This measures how big one cell is.    Esc = cancel",
    "第 2 步 / 共 2 步　點選「{nxt}」那一格的中心（{i}/3）": "Step 2 of 2 — click the centre of the {nxt} cell ({i}/3)",
    "跟著游標的白框就是一格的大小，對準格子中央再按。　　Backspace 退回上一步　　Esc 取消":
        "The white box following the cursor is one cell — line it up on the cell and click.    "
        "Backspace = undo    Esc = cancel",
    "框太小了，請沿著格子的邊框重新拖一次": "That box is too small — drag along the cell's border again",
    "校準盤面（手機截圖）": "Calibrate board (phone screenshot)",
    "沿著左上角那一顆水果的格子邊框拖曳，量出一格有多大。":
        "Drag along the border of the top-left fruit's cell to measure one cell.",
    "第 2 步 / 共 2 步　點「{nxt}」那一格的中心（{i}/3）": "Step 2 of 2 — click the centre of the {nxt} cell ({i}/3)",
    "依序點「右上→右下→左下」三格的中心。Backspace 退回上一步　　Esc 取消":
        "Click the centres of the top-right → bottom-right → bottom-left cells. Backspace = undo    Esc = cancel",
    "已取消校準": "Calibration cancelled",
    "點的位置好像有點歪": "The clicks look a bit off",
    "從上下兩排量到的格距差了 {skew:.0f} px，通常代表有一個角落點偏了。\n\n"
    "還是會先幫你算出來，請在接下來的預覽視窗確認紫色框有沒有套準；沒套準就按「重新框選」再來一次。":
        "The cell spacing measured on the top and bottom rows differs by {skew:.0f} px, which usually "
        "means one corner click was off.\n\nIt will still be calculated — check in the next preview "
        "that the purple boxes sit on the fruits; if not, click \"Redo\" and try again.",
    "抓不到手機畫面：{e}": "Couldn't capture the phone screen: {e}",

    # ---- 確認範圍
    "確認盤面範圍": "Confirm board area",
    "紫色框要剛好套住每一顆水果。不準的話：\n　方向鍵 = 平移 1px　　Shift+方向鍵 = 改變大小　　Ctrl+方向鍵 = 平移 10px":
        "Each purple box should sit right on a fruit. If not:\n  Arrow keys = move 1px    "
        "Shift+arrow = resize    Ctrl+arrow = move 10px",
    "重新自動吸附": "Auto-snap again",
    "重新框選": "Redo",
    "確定": "OK",
    "自動吸附": "Auto-snap",
    "這個範圍看不出格線，請手動微調或重新框選。":
        "Couldn't find grid lines in this area — adjust it manually or redo the selection.",
    "每格 {w:.1f}x{h:.1f}  內縮 {inset:.3f}": "cell {w:.1f}x{h:.1f}  inset {inset:.3f}",
    " 順便鎖定了視窗「{title}」，之後搬動這個視窗不用重新校準。":
        " Also locked onto the window \"{title}\" — you can move it later without recalibrating.",
    "範圍存好了。接著按「② 標記水果」教它每格是幾號。":
        "Area saved. Next, click \"② Label fruits\" and tell it the number in each cell.",
    "範圍存好了，而且馬上就讀得懂盤面 —— 可以開始用了。":
        "Area saved and the board is already readable — you're good to go.",
    "範圍存好了，但有 {n} 格對不上之前學過的樣板（切格位置變了就會這樣）。請按「② 標記水果」重新教一次。":
        "Area saved, but {n} cell(s) don't match the learned fruits (this happens when the cell "
        "positions change). Click \"② Label fruits\" to teach them again.",
    "請先校準盤面": "Calibrate the board first",
    "已重新吸附格線，自動操控接回去了": "Grid re-snapped, auto-play resumed",
    "已重新吸附格線": "Grid re-snapped",
    "吸附失敗，請按「① 校準盤面」重框一次": "Re-snap failed — click \"① Calibrate board\" and mark it again",

    # ---- 標記水果
    "標記水果": "Label fruits",
    "填入每一格水果上的號碼；空格請填 0": "Type the number shown on each fruit; use 0 for empty cells",
    "黃框 = 程式認不得的格子，這幾格一定要填。其他格已經填好目前的判讀，\n"
    "如果判讀是對的就不用動；發現讀錯的話直接改掉，存檔後會一起學進去。":
        "Yellow border = cells the app doesn't recognise; these must be filled in. The other cells "
        "already show its current reading —\nleave them if they're right, or correct any mistakes; "
        "everything is learned when you save.",
    "取消": "Cancel",
    "存檔並開始": "Save & start",
    "第 {r} 列第 {c} 格還沒填": "Row {r}, column {c} is still empty",
    "「{text}」不是數字": "\"{text}\" is not a number",
    "號碼要在 0 到 {max} 之間": "The number must be between 0 and {max}",
    "學到 {added} 張新樣板，樣板庫共 {total} 張": "Learned {added} new template(s), {total} in total",
    "；自動操控接回去了 —— 按 {key} 可隨時停止": "; auto-play resumed — press {key} to stop at any time",

    # ---- 設定
    "設定": "Settings",
    "滑鼠滑動（推薦）": "Mouse swipe (recommended)",
    "鍵盤方向鍵": "Keyboard arrow keys",
    "鍵盤 W A S D": "Keyboard W A S D",
    "PC 模擬器（螢幕擷取）": "PC emulator (screen capture)",
    "手機（USB 接 adb）": "Phone (USB via adb)",
    "思考時間（秒）": "Thinking time (s)",
    "0.2～0.5 就很夠；記得打小數點": "0.2–0.5 is plenty; don't forget the decimal point",
    "偵測間隔（毫秒）": "Detection interval (ms)",
    "多久看一次畫面，全自動可壓到 50": "How often the screen is read; 50 is fine for auto-play",
    "辨識門檻": "Recognition threshold",
    "越小越嚴格；認不得的格子變多就調大": "Lower = stricter; raise it if many cells go unrecognised",
    "取樣內縮比例": "Cell inset ratio",
    "每格四邊往內縮多少，0.05～0.20": "How far each cell is trimmed on every side, 0.05–0.20",
    "視窗透明度": "Window opacity",
    "0.2～1.0": "0.2–1.0",
    "滑動距離比例": "Swipe length ratio",
    "佔盤面短邊的比例，滑不動就調大": "Fraction of the board's short side; raise it if swipes don't register",
    "滑動時間（毫秒）": "Swipe duration (ms)",
    "太快會被遊戲判成點擊": "Too fast and the game treats it as a tap",
    "每步間隔（秒）": "Delay between moves (s)",
    "兩步之間至少隔多久；記得打小數點": "Minimum time between two moves; don't forget the decimal point",
    "偵測與求解": "Detection & solving",
    "自動操控": "Auto-play",
    "操控方式": "Input method",
    "模擬器有設按鍵對應才選鍵盤": "Only pick keyboard if the emulator has key mappings set up",
    "緊急停止鍵": "Emergency stop key",
    "按下去就立刻停手，不用切視窗": "Stops immediately, no need to switch windows",
    "畫面來源": "Screen source",
    "來源": "Source",
    "改這個之後要重新校準一次": "Recalibrate after changing this",
    "手機序號": "Phone serial",
    "adb devices 看到的那串；留白就自動挑唯一一台": "As shown by `adb devices`; leave blank to use the only connected phone",
    "清空樣板庫": "Clear learned fruits",
    "套用": "Apply",
    "會忘掉所有學過的水果外觀，之後要重新標記一次。確定嗎？":
        "This forgets every fruit it has learned and you'll have to label them again. Are you sure?",
    "「{label}」填的「{raw}」不是數字": "\"{label}\": \"{raw}\" is not a number",
    "「{label}」要在 {lo} 到 {hi} 之間（填了 {value}）": "\"{label}\" must be between {lo} and {hi} (got {value})",
    "畫面來源換了，請重新按「① 校準盤面」。": "Screen source changed — click \"① Calibrate board\" again.",
    "樣板庫已清空，請重新標記一次": "Learned fruits cleared — please label them again",
    "設定已套用": "Settings applied",

    # ---- 自動操控
    "已按下 {key}，自動操控停止": "{key} pressed — auto-play stopped",
    "自動操控已停止": "Auto-play stopped",
    "請先按「① 校準盤面」": "Click \"① Calibrate board\" first",
    "請先按「② 標記水果」，程式要看得懂盤面才能自己玩":
        "Click \"② Label fruits\" first — the app has to read the board before it can play",
    "視窗擋住盤面了": "The window is covering the board",
    "這個輔助器的視窗正蓋在遊戲盤面上。\n\n自動操控是用滑鼠在盤面上滑動的，視窗擋著的話會滑到自己身上、"
    "遊戲完全不會有反應。\n\n請先把輔助器視窗拖到旁邊，再按一次「開始自動玩」。":
        "This assistant's window is on top of the game board.\n\nAuto-play swipes on the board with "
        "the mouse; with the window in the way it would swipe on itself and the game wouldn't react."
        "\n\nDrag the assistant aside, then click \"Start auto-play\" again.",
    "在盤面中央用滑鼠滑動": "swipe with the mouse in the middle of the board",
    "按方向鍵": "press the arrow keys",
    "按 W / A / S / D": "press W / A / S / D",
    "開始自動操控": "Start auto-play",
    "接下來程式會自己{how}，一步一步幫你玩。\n\n隨時要停止：\n"
    "　• 按 {key}（不用切回這個視窗也有效）\n　• 或再按一次「■ 停止自動玩」\n\n"
    "開始前請確認模擬器視窗在最上層、沒有被其他視窗擋住。\n\n要開始嗎？":
        "The app will now {how} and play move by move for you.\n\nTo stop at any time:\n"
        "  • press {key} (works without switching to this window)\n  • or click \"■ Stop auto-play\"\n\n"
        "Before starting, make sure the emulator window is on top and not covered by anything.\n\nStart now?",
    "自動操控開始 —— 按 {key} 可隨時停止": "Auto-play started — press {key} to stop at any time",
    "輔助器視窗蓋在盤面上，沒有自動接回去。請把視窗挪開再按「▶ 開始自動玩」。":
        "The assistant's window is covering the board, so auto-play didn't resume. "
        "Move it aside and click \"▶ Start auto-play\".",

    # ---- vision.py / adb.py
    "盤面至少要 2x2": "The board must be at least 2x2",
    "四個角落的相對位置不合理（右邊的點在左邊、或下面的點在上面）。請確認有依照「右上 → 右下 → 左下」的順序點選。":
        "The four corners don't line up (a right point is left of the others, or a bottom point is "
        "above). Make sure you clicked top-right → bottom-right → bottom-left in that order.",
    "找不到 adb。請安裝 Android SDK Platform-Tools（https://developer.android.com/tools/releases/platform-tools），"
    "並確定 adb.exe 在 PATH 上。":
        "adb not found. Install Android SDK Platform-Tools "
        "(https://developer.android.com/tools/releases/platform-tools) and make sure adb.exe is on PATH.",
    "adb 沒回應（{t:.0f} 秒逾時）：{cmd}": "adb didn't respond ({t:.0f} s timeout): {cmd}",
    "執行 adb 失敗：{e}": "Failed to run adb: {e}",
    "裝置「{serial}」狀態是「{state}」，不是「device」（多半要在手機螢幕上按一下允許 USB 偵錯）。":
        "Device \"{serial}\" is \"{state}\", not \"device\" (you probably need to allow USB debugging "
        "on the phone screen).",
    "adb 現在看不到裝置「{serial}」，確認線有接好、手機有開 USB 偵錯。":
        "adb can't see device \"{serial}\" — check the cable and that USB debugging is on.",
    "adb 看得到裝置但都還沒授權：{detail}。檢查手機螢幕，同意「允許 USB 偵錯」。":
        "adb sees device(s) but none are authorised: {detail}. Check the phone screen and allow USB debugging.",
    "adb 沒看到任何裝置。確認手機有接 USB 傳輸線、已開啟「USB 偵錯」。":
        "adb sees no devices. Check the USB cable and that USB debugging is turned on.",
    "adb 看到 {n} 台已授權的裝置，請在設定裡指定要用哪一台的序號：{serials}":
        "adb sees {n} authorised devices — pick one by serial in Settings: {serials}",
}

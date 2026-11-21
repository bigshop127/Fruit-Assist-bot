"""ADB 擷取／操控：跟 vision.ScreenGrabber／control.Controller 介面相容，
換成從 adb 認得到的裝置（USB 接的實體手機）抓畫面、送手勢。

跟 PC 模擬器那條路（mss 截桌面）比，這條路每次擷取都要重新透過 USB 呼叫一次
adb 子行程，實測（Samsung A54，USB 線）一輪 400~460ms，比桌面截圖慢一個數量級。
這是「每一幀都重新啟動 adb」這個機制本身的固有成本，不是這支模組能調的參數；
想要更快只能換掉這個機制（例如常駐裝置端的擷取服務），這版先不做，見 README。
"""

from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image

import control as C
import vision as V
from i18n import tr as _t

# Windows 上跑 subprocess 預設會跳出一個黑色主控台視窗，adb 每次呼叫都跳一下很擾人。
_CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

_DEVICE_LINE = re.compile(r"^(\S+)\s+(\w+)")
_SIZE_LINE = re.compile(r"(\d+)x(\d+)")


class AdbError(OSError):
    """adb 相關的錯誤（找不到 adb、抓不到裝置、screencap 失敗…）。

    是 OSError 的子類別，跟 Engine.step()／_play() 既有的例外處理相容，
    不用另外改那邊的 except 子句。
    """


def find_adb() -> str:
    """找 adb.exe 的路徑：PATH 上有就直接用，沒有就試常見的安裝位置。"""
    found = shutil.which("adb")
    if found:
        return found
    candidates = [
        os.path.expandvars(r"%LOCALAPPDATA%\Android\platform-tools\adb.exe"),
        os.path.expandvars(r"%ANDROID_HOME%\platform-tools\adb.exe"),
        os.path.expandvars(r"%ANDROID_SDK_ROOT%\platform-tools\adb.exe"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    raise AdbError(_t(
        "找不到 adb。請安裝 Android SDK Platform-Tools"
        "（https://developer.android.com/tools/releases/platform-tools），"
        "並確定 adb.exe 在 PATH 上。"
    ))


def _run(adb_path: str, *args: str, timeout: float = 10.0) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            [adb_path, *args], capture_output=True, timeout=timeout,
            creationflags=_CREATE_NO_WINDOW,
        )
    except subprocess.TimeoutExpired as e:
        raise AdbError(_t("adb 沒回應（{t:.0f} 秒逾時）：{cmd}", t=timeout, cmd=" ".join(args))) from e
    except OSError as e:
        raise AdbError(_t("執行 adb 失敗：{e}", e=e)) from e


def list_devices(adb_path: Optional[str] = None) -> List[Tuple[str, str]]:
    """回傳 [(序號, 狀態), ...]。狀態通常是 device／unauthorized／offline。"""
    adb_path = adb_path or find_adb()
    out = _run(adb_path, "devices").stdout.decode("utf-8", "replace")
    devices = []
    for line in out.splitlines()[1:]:
        line = line.strip()
        m = _DEVICE_LINE.match(line)
        if m:
            devices.append((m.group(1), m.group(2)))
    return devices


def pick_device(adb_path: Optional[str] = None, serial: Optional[str] = None) -> str:
    """決定要對哪台裝置下手。

    有指定序號就檢查它在不在、狀態是不是「device」（已授權）；沒指定就在已授權的
    裝置裡挑，剛好一台才自動選——零台或多台都不該用猜的，寧可停下來問清楚。
    """
    adb_path = adb_path or find_adb()
    devices = list_devices(adb_path)
    if serial:
        for s, state in devices:
            if s == serial:
                if state != "device":
                    raise AdbError(_t("裝置「{serial}」狀態是「{state}」，不是「device」"
                                      "（多半要在手機螢幕上按一下允許 USB 偵錯）。",
                                      serial=serial, state=state))
                return serial
        raise AdbError(_t("adb 現在看不到裝置「{serial}」，確認線有接好、手機有開 USB 偵錯。", serial=serial))

    ready = [s for s, state in devices if state == "device"]
    if len(ready) == 1:
        return ready[0]
    if not ready:
        if devices:
            detail = _t("、").join(f"{s}（{state}）" for s, state in devices)
            raise AdbError(_t("adb 看得到裝置但都還沒授權：{detail}。"
                              "檢查手機螢幕，同意「允許 USB 偵錯」。", detail=detail))
        raise AdbError(_t("adb 沒看到任何裝置。確認手機有接 USB 傳輸線、已開啟「USB 偵錯」。"))
    raise AdbError(_t("adb 看到 {n} 台已授權的裝置，請在設定裡指定要用哪一台的序號：{serials}",
                      n=len(ready), serials=", ".join(ready)))


def screen_size(adb_path: str, serial: str) -> Tuple[int, int]:
    """回傳 `wm size` 報的「Physical size」。

    注意：這是面板的**原生（直向）**尺寸，手機轉成橫向玩遊戲時這個數字
    不會跟著轉，會跟 screencap 實際吐出來的畫面方向對不上——AdbGrabber
    因此故意不用這個函式決定擷取範圍，改成直接量一張真的截圖（見
    `AdbGrabber.virtual_screen`）。這裡留著純粹是給想知道面板原生解析度
    的呼叫端用，不要拿它的回傳值去算裁切範圍。
    """
    out = _run(adb_path, "-s", serial, "shell", "wm", "size").stdout.decode("utf-8", "replace")
    m = _SIZE_LINE.search(out)
    if not m:
        raise AdbError(f"讀不到手機解析度（wm size 回傳：{out.strip()!r}）")
    return int(m.group(1)), int(m.group(2))


class AdbGrabber:
    """跟 vision.ScreenGrabber 介面相容，換成從手機抓畫面。

    adb 路徑跟裝置序號都是懶得決定的——建構子只存設定，真正去找 adb.exe、
    挑裝置是在第一次真的要抓畫面時才做，失敗就丟 AdbError（是 OSError），
    Engine.step() 既有的例外處理會接住轉成畫面上的錯誤訊息，不會讓
    Engine.rebuild() 因為手機還沒接上就整個炸掉。
    """

    def __init__(self, serial: Optional[str] = None, adb_path: Optional[str] = None) -> None:
        self.backend = "adb"
        self._adb_path = adb_path
        self._serial = serial
        self._resolved_serial: Optional[str] = None

    def _resolve(self) -> Tuple[str, str]:
        path = self._adb_path or find_adb()
        self._adb_path = path
        if self._resolved_serial is None:
            self._resolved_serial = pick_device(path, self._serial)
        return path, self._resolved_serial

    def _screencap(self) -> np.ndarray:
        path, serial = self._resolve()
        proc = _run(path, "-s", serial, "exec-out", "screencap", "-p", timeout=8.0)
        if proc.returncode != 0 or not proc.stdout:
            raise AdbError(f"screencap 失敗：{proc.stderr.decode('utf-8', 'replace').strip()}")
        try:
            img = Image.open(io.BytesIO(proc.stdout)).convert("RGB")
        except Exception as e:
            raise AdbError(f"screencap 回傳的資料不是有效圖片：{e}") from e
        return np.asarray(img)

    def virtual_screen(self) -> V.Region:
        """回傳目前這張截圖實際的寬高。

        故意不用 `wm size`（見 `screen_size` 的說明）——那個數字是面板原生
        方向，手機轉成橫向玩的話會跟真正截出來的畫面對不上，裁切範圍就會
        「超出畫面」。抓一張真的截圖來量，保證跟等一下 grab() 看到的一致。
        """
        h, w = self._screencap().shape[:2]
        return V.Region(0, 0, w, h)

    def grab(self, region: V.Region) -> np.ndarray:
        if region.width <= 0 or region.height <= 0:
            raise ValueError(f"擷取範圍不合法：{region}")
        full = self._screencap()
        h, w = full.shape[:2]
        # 故意不夾住裁切範圍——手機解析度跟校準當下不一樣時（例如換了台裝置、
        # 螢幕轉向），裁出一塊尺寸不對的畫面丟給後面的格線辨識，只會產生一個
        # 看起來詭異的誤判，不如在這裡就直接講清楚「範圍對不上畫面」。
        if region.left < 0 or region.top < 0 or region.right > w or region.bottom > h:
            raise ValueError(f"擷取範圍超出手機畫面：{region}（手機畫面 {w}x{h}）")
        return full[region.top:region.bottom, region.left:region.right]


class AdbController:
    """跟 control.Controller 介面相容，換成用 `adb shell input swipe` 操控。

    起訖點的幾何算法直接借 control.swipe_points（純函式，region 進 region 出，
    不管背後是螢幕座標還是手機像素），失敗一律丟 control.InputError，
    Engine._play() 既有的例外處理會接住。
    """

    def __init__(self, serial: Optional[str] = None, adb_path: Optional[str] = None,
                 duration: float = 0.14, fraction: float = 0.35) -> None:
        self._adb_path = adb_path
        self._serial = serial
        self._resolved_serial: Optional[str] = None
        self.duration = duration
        self.fraction = fraction

    def _resolve(self) -> Tuple[str, str]:
        path = self._adb_path or find_adb()
        self._adb_path = path
        if self._resolved_serial is None:
            self._resolved_serial = pick_device(path, self._serial)
        return path, self._resolved_serial

    def play(self, region: V.Region, move: int) -> None:
        try:
            path, serial = self._resolve()
        except AdbError as e:
            raise C.InputError(str(e)) from e
        x0, y0, x1, y1 = C.swipe_points(region, move, self.fraction)
        ms = max(50, int(self.duration * 1000))
        proc = _run(path, "-s", serial, "shell", "input", "swipe",
                    str(x0), str(y0), str(x1), str(y1), str(ms), timeout=8.0)
        if proc.returncode != 0:
            raise C.InputError(f"adb 送滑動失敗：{proc.stderr.decode('utf-8', 'replace').strip()}")


# ---------------------------------------------------------------- 模擬器背景滑動

def _gray(img: np.ndarray) -> np.ndarray:
    img = np.asarray(img, dtype=np.float32)
    if img.ndim == 3:
        img = img[..., :3] @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    return img


def _resize(gray: np.ndarray, w: int, h: int) -> np.ndarray:
    im = Image.fromarray(gray.astype(np.float32), mode="F")
    return np.asarray(im.resize((max(1, w), max(1, h)), Image.BILINEAR), dtype=np.float32)


def _ncc_map(image: np.ndarray, tmpl: np.ndarray) -> np.ndarray:
    """標準化互相關（FFT 版），回傳每個左上角位置的分數（-1～1）。"""
    H, W = image.shape
    h, w = tmpl.shape
    t = tmpl - tmpl.mean()
    t_norm = float(np.sqrt((t * t).sum()))
    if t_norm < 1e-6:
        return np.full((H - h + 1, W - w + 1), -1.0, dtype=np.float32)
    shape = (H, W)
    corr = np.fft.irfft2(np.fft.rfft2(image, shape) * np.conj(np.fft.rfft2(t, shape)), shape)
    corr = corr[:H - h + 1, :W - w + 1]

    def box(a: np.ndarray) -> np.ndarray:
        c = np.pad(a, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
        return c[h:, w:] - c[:-h, w:] - c[h:, :-w] + c[:-h, :-w]

    n = h * w
    s1 = box(image.astype(np.float64))
    s2 = box(image.astype(np.float64) ** 2)
    var = s2 - s1 * s1 / n
    # 幾乎單色的區域（背景、黑邊）分母趨近 0，算出來的分數會爆表，直接排除
    flat = var < n * 4.0
    score = corr / (np.sqrt(np.maximum(var, 1e-6)) * t_norm)
    score[flat] = -1.0
    return np.clip(score, -1.0, 1.0).astype(np.float32)


def locate_board(device_img: np.ndarray, board_img: np.ndarray,
                 work: int = 480) -> Tuple[V.Region, float]:
    """在模擬器自己的截圖（裝置像素）裡找出盤面在哪。

    輔助器是在 PC 螢幕上框盤面的，adb 送手勢卻要用模擬器內部的像素座標，
    兩者差一個縮放＋位移，而且會隨模擬器視窗大小、BlueStacks 側邊欄、標題列
    改變。與其去猜視窗版面，不如直接拿「螢幕上那塊盤面」去模擬器截圖裡比對：
    多個縮放比例各做一次標準化互相關，取分數最高的。回傳 (裝置座標範圍, 分數)。
    """
    dev = _gray(device_img)
    brd = _gray(board_img)
    H, W = dev.shape
    f = work / max(H, W)
    small = _resize(dev, int(W * f), int(H * f))
    sh, sw = small.shape
    bh, bw = brd.shape

    best = (-2.0, 0, 0, 1.0)
    scale = 0.25
    while scale <= 5.0:
        tw, th = int(round(bw * scale * f)), int(round(bh * scale * f))
        if 16 <= tw <= sw and 16 <= th <= sh:
            score_map = _ncc_map(small, _resize(brd, tw, th))
            idx = int(np.argmax(score_map))
            y, x = divmod(idx, score_map.shape[1])
            score = float(score_map[y, x])
            if score > best[0]:
                best = (score, x, y, scale)
        scale *= 1.03

    score, x, y, scale = best
    region = V.Region(int(round(x / f)), int(round(y / f)),
                      int(round(bw * scale)), int(round(bh * scale)))
    return region, score


class EmulatorAdbController:
    """PC 模擬器（BlueStacks 等）用 adb 送滑動，不碰真的滑鼠、不搶焦點。

    畫面還是從 PC 螢幕截（快），只有「滑」改走 adb。第一次滑之前抓一張
    模擬器截圖，用 locate_board 找出盤面在模擬器裡的位置並記住；盤面大小
    （校準）變了、或連續滑了沒反應時重新找。
    """

    MIN_SCORE = 0.55
    _cache: dict = {}   # (序號, 盤面寬, 盤面高) → 裝置座標範圍；換校準才會失效

    def __init__(self, serial: str, board_provider, adb_path: Optional[str] = None,
                 duration: float = 0.14, fraction: float = 0.35) -> None:
        self.serial = serial
        self.board_provider = board_provider    # 回傳目前螢幕上那塊盤面的影像
        self._adb_path = adb_path
        self._connected = False
        self.duration = duration
        self.fraction = fraction

    def _path(self) -> str:
        if self._adb_path is None:
            self._adb_path = find_adb()
        if not self._connected and ":" in self.serial:
            # 127.0.0.1:5565 這種網路序號要先 connect 一次（已連上的話是無害的）
            _run(self._adb_path, "connect", self.serial, timeout=8.0)
            self._connected = True
        return self._adb_path

    def _key(self, region: V.Region) -> tuple:
        return (self.serial, region.width, region.height)

    def forget(self) -> None:
        for k in [k for k in self._cache if k[0] == self.serial]:
            del self._cache[k]

    def device_region(self, region: V.Region) -> V.Region:
        key = self._key(region)
        if key in self._cache:
            return self._cache[key]
        path = self._path()
        proc = _run(path, "-s", self.serial, "exec-out", "screencap", "-p", timeout=8.0)
        if proc.returncode != 0 or not proc.stdout:
            raise AdbError(_t("抓不到模擬器畫面（adb {serial}）：{err}", serial=self.serial,
                              err=proc.stderr.decode("utf-8", "replace").strip()))
        dev = np.asarray(Image.open(io.BytesIO(proc.stdout)).convert("RGB"))
        board = self.board_provider()
        if board is None:
            raise AdbError(_t("還沒抓到盤面畫面，等一下再試"))
        found, score = locate_board(dev, board)
        if score < self.MIN_SCORE:
            raise AdbError(_t("在模擬器畫面裡找不到盤面（相似度 {score:.2f}）。確認 adb 連的是正在玩的那個模擬器（{serial}）。",
                              score=score, serial=self.serial))
        self._cache[key] = found
        return found

    def play(self, region: V.Region, move: int) -> None:
        try:
            dev_region = self.device_region(region)
            path = self._path()
        except AdbError as e:
            raise C.InputError(str(e)) from e
        x0, y0, x1, y1 = C.swipe_points(dev_region, move, self.fraction)
        ms = max(50, int(self.duration * 1000))
        proc = _run(path, "-s", self.serial, "shell", "input", "swipe",
                    str(x0), str(y0), str(x1), str(y1), str(ms), timeout=8.0)
        if proc.returncode != 0:
            raise C.InputError(_t("adb 送滑動失敗：{err}",
                                  err=proc.stderr.decode("utf-8", "replace").strip()))


__all__ = [
    "AdbError", "AdbGrabber", "AdbController", "EmulatorAdbController", "locate_board",
    "find_adb", "list_devices", "pick_device", "screen_size",
]

"""adb.py 的驗證。

這支測試全程用假的 `_run`（monkeypatch），不需要真的裝 adb、也不需要接手機——
邏輯本身（裝置狀態怎麼判斷、擷取範圍怎麼裁切、失敗要丟哪種例外）都能在沒有
真實裝置的機器上測。實機（Samsung A54，USB）驗證另外用手動腳本跑過，不放進
這支自動化測試裡，因為別台機器不會接著同一支手機。

    python test_adb.py
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
from typing import List

import numpy as np
from PIL import Image

# 這支測試會比對中文訊息字樣，固定用中文介面跑（英文版由 test_i18n.py 負責）
os.environ["FRUIT2048_LANG"] = "zh"

import adb as ADB  # noqa: E402
import control as C
import vision as V

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_failures = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{'  ' + detail if detail else ''}")
    if not ok:
        _failures.append(name)
    return ok


class FakeRun:
    """取代 adb._run：依呼叫順序回傳預先排好的結果，順便記錄實際下了什麼指令。"""

    def __init__(self, scripted: List[tuple]) -> None:
        self.scripted = list(scripted)   # [(returncode, stdout_bytes, stderr_bytes), ...]
        self.calls: List[tuple] = []

    def __call__(self, adb_path, *args, timeout=10.0):
        self.calls.append(args)
        if not self.scripted:
            raise AssertionError(f"沒有預先安排的回應了，但又被呼叫：{args}")
        code, out, err = self.scripted.pop(0)
        return subprocess.CompletedProcess(args=list(args), returncode=code,
                                            stdout=out, stderr=err)


def png_bytes(w: int, h: int, fill=(30, 60, 90)) -> bytes:
    img = Image.new("RGB", (w, h), fill)
    # 塗一格看得出方向的標記，裁切測試才有辦法驗證裁對了地方
    for x in range(min(5, w)):
        for y in range(min(5, h)):
            img.putpixel((x, y), (255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main():
    print("1) list_devices：解析 `adb devices` 的輸出")
    real_run = ADB._run
    try:
        ADB._run = FakeRun([
            (0, b"List of devices attached\nABC123\tdevice\nXYZ999\tunauthorized\n\n", b""),
        ])
        devices = ADB.list_devices("adb")
        check("解析出兩台裝置", devices == [("ABC123", "device"), ("XYZ999", "unauthorized")],
              f"{devices}")

        ADB._run = FakeRun([(0, b"List of devices attached\n", b"")])
        check("沒有裝置回空清單", ADB.list_devices("adb") == [])
    finally:
        ADB._run = real_run

    print("2) pick_device：怎麼決定要對哪台裝置下手")
    def with_devices(pairs):
        return FakeRun([(0, ("List of devices attached\n" +
                             "\n".join(f"{s}\t{st}" for s, st in pairs)).encode(), b"")])

    try:
        ADB._run = with_devices([("ABC123", "device")])
        check("剛好一台已授權 → 自動選中", ADB.pick_device("adb") == "ABC123")

        ADB._run = with_devices([("ABC123", "device"), ("DEF456", "device")])
        try:
            ADB.pick_device("adb")
            check("多台已授權要停下來問，不能亂猜", False)
        except ADB.AdbError as e:
            check("多台已授權要停下來問，不能亂猜", "2 台" in str(e), str(e))

        ADB._run = with_devices([("XYZ999", "unauthorized")])
        try:
            ADB.pick_device("adb")
            check("只有未授權裝置要講清楚原因", False)
        except ADB.AdbError as e:
            check("只有未授權裝置要講清楚原因", "授權" in str(e), str(e))

        ADB._run = with_devices([])
        try:
            ADB.pick_device("adb")
            check("完全沒裝置要講清楚原因", False)
        except ADB.AdbError as e:
            check("完全沒裝置要講清楚原因", "沒看到任何裝置" in str(e), str(e))

        ADB._run = with_devices([("ABC123", "device"), ("DEF456", "device")])
        check("有指定序號就用指定的，不管還有誰在", ADB.pick_device("adb", "DEF456") == "DEF456")

        ADB._run = with_devices([("ABC123", "unauthorized")])
        try:
            ADB.pick_device("adb", "ABC123")
            check("指定的序號狀態不是 device 要擋下來", False)
        except ADB.AdbError as e:
            check("指定的序號狀態不是 device 要擋下來", "unauthorized" in str(e), str(e))

        ADB._run = with_devices([("ABC123", "device")])
        try:
            ADB.pick_device("adb", "NOPE")
            check("指定的序號根本不存在要講清楚", False)
        except ADB.AdbError as e:
            check("指定的序號根本不存在要講清楚", "NOPE" in str(e), str(e))
    finally:
        ADB._run = real_run

    print("3) screen_size：解析 `wm size`")
    try:
        ADB._run = FakeRun([(0, b"Physical size: 1080x2340\n", b"")])
        check("解析出手機解析度", ADB.screen_size("adb", "ABC123") == (1080, 2340))

        ADB._run = FakeRun([(0, b"???\n", b"")])
        try:
            ADB.screen_size("adb", "ABC123")
            check("格式不對要講清楚，不要裝沒事", False)
        except ADB.AdbError:
            check("格式不對要講清楚，不要裝沒事", True)
    finally:
        ADB._run = real_run

    # AdbGrabber/AdbController 是懶得解析裝置的：第一次真的呼叫 grab()/play() 時
    # 才會內部呼叫一次 pick_device()（也就是多打一次 `adb devices`），解析出來的
    # 序號會快取住，同一個物件之後就不會再問一次。每個新物件的第一次呼叫都要
    # 多排一組「裝置清單」的回應在最前面，之後的呼叫才只需要排真正要測的那個回應。
    DEVICES_ONE = (0, b"List of devices attached\nABC123\tdevice\n", b"")

    print("4) AdbGrabber：擷取＋裁切")
    try:
        png = png_bytes(200, 150)
        g = ADB.AdbGrabber(serial="ABC123", adb_path="adb")

        ADB._run = FakeRun([DEVICES_ONE, (0, png, b"")])
        full = g.grab(V.Region(0, 0, 200, 150))
        check("整張抓下來大小對", full.shape[:2] == (150, 200), f"{full.shape}")
        check("紅色標記在左上角，裁切方向沒錯", tuple(full[0, 0]) == (255, 0, 0), f"{full[0,0]}")

        # 手機轉成橫向玩遊戲時，wm size 報的「面板原生尺寸」是直向的，
        # 跟這時候 screencap 實際吐出來的橫向畫面對不上——這正是使用者
        # 第一次校準就撞到的真實案例（wm size 說 1080x2340，screencap
        # 卻是 2340x1080）。virtual_screen() 一定要用真的截圖量，不能問
        # wm size，這裡就是回歸測試。
        landscape = png_bytes(2340, 1080)
        ADB._run = FakeRun([(0, landscape, b"")])
        vs = g.virtual_screen()
        check("virtual_screen 用真的截圖量尺寸，不是問 wm size",
              (vs.width, vs.height) == (2340, 1080), f"{vs}")
        check("virtual_screen 只需要一次呼叫（截圖本身），沒有多打 wm size",
              len(ADB._run.calls) == 1 and ADB._run.calls[0][2:5] == ("exec-out", "screencap", "-p"),
              f"{ADB._run.calls}")

        ADB._run = FakeRun([(0, png, b"")])   # 序號已經快取了，這次不用再問一次裝置清單
        cropped = g.grab(V.Region(50, 40, 60, 30))
        check("裁切出來的大小對", cropped.shape[:2] == (30, 60), f"{cropped.shape}")
        check("裁切出來的內容對得上原圖同一個位置",
              np.array_equal(cropped, full[40:70, 50:110]))

        try:
            g.grab(V.Region(0, 0, -5, 10))
            check("非法範圍（負寬）擋下來", False)
        except ValueError:
            check("非法範圍（負寬）擋下來", True)

        ADB._run = FakeRun([(1, b"", b"Error: something broke")])
        try:
            g.grab(V.Region(0, 0, 10, 10))
            check("screencap 失敗要轉成清楚的錯誤", False)
        except ADB.AdbError as e:
            check("screencap 失敗要轉成清楚的錯誤", "something broke" in str(e), str(e))
            check("AdbError 是 OSError，跟 Engine 既有的例外處理相容", isinstance(e, OSError))

        ADB._run = FakeRun([(0, b"not a png at all", b"")])
        try:
            g.grab(V.Region(0, 0, 10, 10))
            check("回傳的不是圖片要講清楚，不要整個炸掉", False)
        except ADB.AdbError:
            check("回傳的不是圖片要講清楚，不要整個炸掉", True)

        g2 = ADB.AdbGrabber(serial="ABC123", adb_path="adb")
        ADB._run = FakeRun([DEVICES_ONE, (0, png_bytes(50, 50), b"")])
        try:
            g2.grab(V.Region(0, 0, 999, 999))
            check("要求的範圍超出手機畫面要擋下來", False)
        except ValueError as e:
            check("要求的範圍超出手機畫面要擋下來", "超出" in str(e), str(e))
    finally:
        ADB._run = real_run

    print("5) AdbController：滑動指令組得對、失敗轉成 control.InputError")
    try:
        ctl = ADB.AdbController(serial="ABC123", adb_path="adb", duration=0.2, fraction=0.35)
        region = V.Region(0, 0, 400, 400)

        runner = FakeRun([DEVICES_ONE, (0, b"", b"")])
        ADB._run = runner
        import solver as S
        ctl.play(region, S.RIGHT)
        cmd = runner.calls[-1]
        check("指令是 shell input swipe", cmd[:4] == ("-s", "ABC123", "shell", "input"),
              f"{cmd}")
        check("滑動時間換算成毫秒", cmd[-1] == "200", f"{cmd}")
        x0, y0, x1, y1 = C.swipe_points(region, S.RIGHT, 0.35)
        check("起訖點座標跟 swipe_points 算的一樣",
              cmd[5:9] == (str(x0), str(y0), str(x1), str(y1)), f"{cmd}")

        ADB._run = FakeRun([(1, b"", b"device offline")])
        try:
            ctl.play(region, S.RIGHT)
            check("送滑動失敗要轉成 control.InputError（Engine._play 只接這個）", False)
        except C.InputError as e:
            check("送滑動失敗要轉成 control.InputError（Engine._play 只接這個）",
                  "device offline" in str(e), str(e))
    finally:
        ADB._run = real_run

    print("6) find_adb：PATH 上找得到就直接用")
    import shutil as _shutil
    real_which = _shutil.which
    try:
        _shutil.which = lambda name: "C:\\fake\\adb.exe" if name == "adb" else None
        check("PATH 上有就回傳那個路徑", ADB.find_adb() == "C:\\fake\\adb.exe")
    finally:
        _shutil.which = real_which

    print("7) 模擬器背景滑動：在模擬器截圖裡找出盤面、照裝置座標送 input swipe")
    shot = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "testdata", "board.png")).convert("RGB")
    l, t, r, b = 41, 35, 746, 750
    screen_board = np.asarray(shot.crop((l, t, r, b)).resize((448, 454)))   # 螢幕上看到的盤面
    for sc, (ox, oy), (W, H) in [(1.0, (120, 300), (900, 1600)), (0.45, (400, 200), (1600, 900))]:
        dev = Image.new("RGB", (W, H), (40, 60, 90))
        dev.paste(shot.resize((int(shot.width * sc), int(shot.height * sc))), (ox, oy))
        got, score = ADB.locate_board(np.asarray(dev), screen_board)
        want = (ox + l * sc, oy + t * sc, (r - l) * sc, (b - t) * sc)
        err = max(abs(a - w) for a, w in zip(got, want))
        check(f"縮放 {sc}：找到的位置誤差 ≤ 6px、分數夠高", err <= 6 and score > 0.8,
              f"got={tuple(got)} want={tuple(int(v) for v in want)} score={score:.2f}")

    dev = Image.new("RGB", (900, 1600), (40, 60, 90))
    dev.paste(shot, (120, 300))
    buf = io.BytesIO()
    dev.save(buf, format="PNG")
    real_run = ADB._run
    real_port_open = ADB._port_open
    try:
        ADB.EmulatorAdbController._cache.clear()
        devs = (0, b"List of devices attached\n127.0.0.1:5565\tdevice\n", b"")
        fake = FakeRun([(0, b"connected to 127.0.0.1:5565", b""), devs, (0, buf.getvalue(), b""), (0, b"", b""), (0, b"", b"")])
        ADB._run = fake
        ADB._port_open = lambda serial, timeout=0.3: True   # 不要真的去敲本機的埠
        ctl = ADB.EmulatorAdbController("127.0.0.1:5565", lambda: screen_board,
                                        adb_path="adb", duration=0.15)
        screen_region = V.Region(500, 400, 448, 454)
        ctl.play(screen_region, S.LEFT)
        ctl.play(screen_region, S.LEFT)
        cmds = [c for c in fake.calls]
        check("網路序號會先 adb connect", cmds[0] == ("connect", "127.0.0.1:5565"), f"{cmds[0]}")
        check("只截一次圖（位置有記住）",
              sum(1 for c in cmds if "screencap" in c) == 1, f"{cmds}")
        swipe = cmds[3]
        x0, y0, x1, y1 = (int(v) for v in swipe[5:9])
        check("滑動在裝置座標、落在盤面裡、往左",
              161 <= x1 < x0 <= 866 and 335 <= y0 <= 1050 and y0 == y1, f"{swipe}")

        ADB.EmulatorAdbController._cache.clear()
        blank = io.BytesIO()
        Image.new("RGB", (900, 1600), (40, 60, 90)).save(blank, format="PNG")
        ADB._run = FakeRun([(0, blank.getvalue(), b"")])
        ctl._connected = True
        try:
            ctl.play(screen_region, S.LEFT)
            check("找不到盤面要轉成 InputError", False)
        except C.InputError as e:
            check("找不到盤面要轉成 InputError", "找不到盤面" in str(e), str(e))
    finally:
        ADB._run = real_run
        ADB._port_open = real_port_open
        ADB.EmulatorAdbController._cache.clear()

    print("8) 模擬器（網路序號）：先 adb connect、擷取走原始格式")
    import struct
    w, h = 6, 4
    px = np.zeros((h, w, 4), np.uint8)
    px[0, 0] = (255, 0, 0, 255)
    px[3, 5] = (0, 0, 255, 255)
    for hdr in (struct.pack("<4I", w, h, 1, 0), struct.pack("<3I", w, h, 1)):
        img = ADB.decode_raw_screencap(hdr + px.tobytes())
        check(f"原始格式解得出來（表頭 {len(hdr)} bytes）",
              img.shape == (h, w, 3) and tuple(img[0, 0]) == (255, 0, 0) and tuple(img[3, 5]) == (0, 0, 255))
    try:
        ADB.decode_raw_screencap(b"garbage-garbage")
        check("壞掉的原始資料要丟 AdbError", False)
    except ADB.AdbError:
        check("壞掉的原始資料要丟 AdbError", True)

    real_run = ADB._run
    try:
        raw = struct.pack("<4I", w, h, 1, 0) + px.tobytes()
        fake = FakeRun([(0, b"connected to 127.0.0.1:5565", b""), (0, b"List of devices attached\n127.0.0.1:5565\tdevice\n", b""),
                        (0, raw, b"")])
        ADB._run = fake
        ADB._port_open = lambda serial, timeout=0.3: True
        g = ADB.AdbGrabber(serial="127.0.0.1:5565", adb_path="adb")
        img = g.grab(V.Region(0, 0, w, h))
        check("先 connect 再挑裝置", fake.calls[0] == ("connect", "127.0.0.1:5565"), f"{fake.calls}")
        check("網路序號擷取不加 -p", fake.calls[2] == ("-s", "127.0.0.1:5565", "exec-out", "screencap"),
              f"{fake.calls[2]}")
        check("擷取結果正確", img.shape == (h, w, 3))
    finally:
        ADB._run = real_run
        ADB._port_open = real_port_open

    print("9) 換了模擬器實例：設定的位址連不上就找唯一開著的那台；解析度不同就照比例縮放")
    real = (ADB._try_connect, ADB._emulator_ports)
    try:
        ADB._REDIRECT.clear()
        alive = {"127.0.0.1:5555"}
        ADB._try_connect = lambda path, serial: serial in alive
        ADB._emulator_ports = lambda: [5555, 5565, 5575]
        check("設定 5565、只有 5555 開著 → 改用 5555",
              ADB.resolve_network_serial("adb", "127.0.0.1:5565") == "127.0.0.1:5555")
        alive = {"127.0.0.1:5565"}
        check("原本那台又開了 → 回到原本那台",
              ADB.resolve_network_serial("adb", "127.0.0.1:5565") == "127.0.0.1:5565")
        alive = {"127.0.0.1:5555", "127.0.0.1:5575"}
        ADB._REDIRECT.clear()
        check("設定的那台關著、另外好幾台開著 → 先挑一台（盤面不在那台會再換）",
              ADB.resolve_network_serial("adb", "127.0.0.1:5565") in alive)
        alive = set()
        try:
            ADB.resolve_network_serial("adb", "127.0.0.1:5565")
            check("都沒開 → 清楚的錯誤", False)
        except ADB.AdbError as e:
            check("都沒開 → 清楚的錯誤", "5565" in str(e), str(e))
    finally:
        ADB._try_connect, ADB._emulator_ports = real
        ADB._REDIRECT.clear()

    g = ADB.AdbGrabber(serial="127.0.0.1:5565", reference_size=(1600, 900))
    region = V.Region(470, 182, 649, 641)
    g.last_size = (1600, 900)
    check("解析度一樣 → 範圍不變", g.map_region(region) == region)
    g.last_size = (1280, 720)
    check("1600x900 校準、換到 1280x720 → 照比例縮成 0.8 倍",
          g.map_region(region) == V.Region(376, 146, 519, 513), f"{g.map_region(region)}")
    check("沒記錄校準大小 → 不縮放（舊設定檔相容）",
          ADB.AdbGrabber(serial="x:1").map_region(region) == region)

    print("10) 「1」「2」兩台模擬器同時開著：看哪一台畫面上真的有盤面就用哪一台，滑動也跟著換")
    real = (ADB._try_connect, ADB._emulator_ports)
    try:
        ADB._REDIRECT.clear()
        ADB._try_connect = lambda path, serial: serial in ("127.0.0.1:5555", "127.0.0.1:5565")
        ADB._emulator_ports = lambda: [5555, 5565]
        board_px = np.full((720, 1280, 3), 200, np.uint8)     # 「2」號：盤面在這
        city_px = np.zeros((900, 1600, 3), np.uint8)          # 「1」號：在主城
        shots = {"127.0.0.1:5555": city_px, "127.0.0.1:5565": board_px}
        g = ADB.AdbGrabber(serial="127.0.0.1:5555", adb_path="adb", reference_size=(1600, 900))
        g._resolved_serial = "127.0.0.1:5555"
        g._screencap_from = lambda path, serial: shots[serial]
        region = V.Region(470, 182, 649, 641)
        found = g.find_board_instance(region, lambda crop: crop.mean() > 100)
        check("換到畫面上有盤面的那台", found == "127.0.0.1:5565" and g.serial == "127.0.0.1:5565", f"{found}")
        check("換過去之後照那台的解析度縮放", g.last_size == (1280, 720)
              and g.map_region(region) == V.Region(376, 146, 519, 513), f"{g.map_region(region)}")
        ctl = ADB.AdbController(serial="127.0.0.1:5555", adb_path="adb",
                                serial_provider=lambda: g.serial, region_mapper=g.map_region)
        real_run = ADB._run
        fake = FakeRun([(0, b"", b"")])
        ADB._run = fake
        try:
            ctl.play(region, S.LEFT)
        finally:
            ADB._run = real_run
        check("滑動送到同一台（2 號）", fake.calls[0][:2] == ("-s", "127.0.0.1:5565"), f"{fake.calls}")
        check("哪一台都沒有盤面 → 不亂換",
              g.find_board_instance(region, lambda crop: False) is None and g.serial == "127.0.0.1:5565")
    finally:
        ADB._try_connect, ADB._emulator_ports = real
        ADB._REDIRECT.clear()

    print()
    if _failures:
        print(f"有 {len(_failures)} 項失敗 ❌")
        for f in _failures:
            print(f"  - {f}")
        return 1
    print("全部通過 ✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

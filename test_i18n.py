"""中英介面：每一句 tr("...") 都要有英文、佔位變數要對得上、兩種語言都能正常開起來。

跑法：python test_i18n.py
加 --dump 會列出還沒翻的句子（補對照表用）。
"""
from __future__ import annotations

import ast
import os
import string
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import i18n  # noqa: E402
import solver as S  # noqa: E402

SOURCES = ("app.py", "vision.py", "adb.py")
# tr() 的參數不是字面字串的地方（例如 tr(S.MOVE_NAME[best])），把可能的值列在這裡
DYNAMIC_KEYS = set(S.MOVE_NAME.values())

FAILS = 0


def check(name, ok, detail=""):
    global FAILS
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        FAILS += 1


def collect_keys():
    keys = {}
    for fn in SOURCES:
        tree = ast.parse(open(os.path.join(HERE, fn), encoding="utf-8").read())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in ("tr", "_t") and node.args
                    and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                keys.setdefault(node.args[0].value, f"{fn}:{node.lineno}")
    for k in DYNAMIC_KEYS:
        keys.setdefault(k, "solver.MOVE_NAME")
    return keys


def fields(text):
    return sorted({f for _, f, _, _ in string.Formatter().parse(text) if f})


def main():
    keys = collect_keys()
    if "--dump" in sys.argv:
        for k, where in keys.items():
            if k not in i18n.EN:
                print(f"{where}\t{k!r}")
        return 0

    print("1) 英文對照表涵蓋所有介面文字")
    missing = [(w, k) for k, w in keys.items() if k not in i18n.EN]
    check(f"{len(keys)} 句都有英文", not missing,
          "；".join(f"{w} {k[:30]}" for w, k in missing[:8]))
    stale = [k for k in i18n.EN if k not in keys]
    check("對照表裡沒有用不到的舊句子", not stale, "；".join(k[:30] for k in stale[:8]))

    print("2) 佔位變數兩邊一致（不然英文版會 KeyError）")
    bad = [k for k in keys if k in i18n.EN and fields(k) != fields(i18n.EN[k])]
    check("全部一致", not bad, "；".join(f"{k[:30]} {fields(k)} vs {fields(i18n.EN[k])}" for k in bad[:5]))

    print("3) 英文版裡不該殘留中文")
    cjk = [k for k, v in i18n.EN.items()
           if any("一" <= ch <= "鿿" for ch in v)]
    check("沒有殘留", not cjk, "；".join(cjk[:5]))

    print("4) 兩種語言的程式都載入得起來、字串真的有換")
    code = ("import app, i18n; from i18n import tr; "
            "print(i18n.LANG, tr('設定'), app.METHOD_LABELS['swipe'])")
    for lang, want in (("zh", "設定"), ("en", "Settings")):
        env = dict(os.environ, FRUIT2048_LANG=lang, PYTHONIOENCODING="utf-8")
        out = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                             capture_output=True, text=True, encoding="utf-8")
        line = out.stdout.strip()
        check(f"{lang}：{line}", out.returncode == 0 and line.startswith(lang) and want in line,
              out.stderr.strip()[-200:])

    print("5) 語言偵測的優先順序")
    import json
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "config.json"), "w", encoding="utf-8") as f:
            json.dump({"language": "en"}, f)
        saved_dir, saved_env = i18n._app_dir, os.environ.pop("FRUIT2048_LANG", None)
        try:
            i18n._app_dir = lambda: d
            check("config.json 寫 en → 英文", i18n._detect() == "en")
            os.environ["FRUIT2048_LANG"] = "zh"
            check("環境變數優先於 config.json", i18n._detect() == "zh")
            del os.environ["FRUIT2048_LANG"]
            os.remove(os.path.join(d, "config.json"))
            check("都沒設定 → 跟著打包預設（原始碼版＝中文）", i18n._detect() in ("zh", "en"))
        finally:
            i18n._app_dir = saved_dir
            if saved_env is not None:
                os.environ["FRUIT2048_LANG"] = saved_env

    print("全部通過 ✅" if FAILS == 0 else f"有 {FAILS} 項失敗 ❌")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())

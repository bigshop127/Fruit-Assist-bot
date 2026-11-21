"""魚符計算的驗證。    python test_fishcalc.py"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import fishcalc as F

_failures = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{'  ' + detail if detail else ''}")
    if not ok:
        _failures.append(name)


def main():
    check("兩個 1 合一個 2", F.plan([1, 1], 0).best_level == 2)
    check("四個 1 合一個 3", F.plan([1, 1, 1, 1], 0).best_level == 3)
    check("一顆 1 加 3 個魚符也是 3", F.plan([1], 3).best_level == 3)

    p = F.plan([1], 0)
    check("只有一顆 1：下一個目標是 2 號、還要 1 個魚符",
          p.targets[0].label_level == 2 and p.targets[0].fish_needed == 1, f"{p.targets[0]}")

    # 使用者 2026-11-21 的截圖：盤面 1,5,11,12 / 2,3,2,2 / 3,1 / 2,1，魚符 1126
    board = [1, 5, 11, 12, 2, 3, 2, 2, 3, 1, 0, 0, 2, 1, 0, 0]
    p = F.plan(board, 1126)
    check("截圖盤面總值 3107", p.board == 3107, str(p.board))
    check("加 1126 魚符 → 理論上兩顆 12 號、多 137",
          (p.best_level, p.best_count, p.leftover) == (12, 2, 137), f"{p}")
    t = p.targets[0]
    check("第三顆 12 號要 3037 魚符、還差 1911",
          (t.label_level, t.count, t.fish_needed, t.short) == (12, 3, 3037, 1911), f"{t}")

    p = F.plan([5], 20)
    check("5 號＋20 魚符＝36 → 6 號、多 4", (p.best_level, p.leftover) == (6, 4), f"{p}")
    check("7 號要 48 魚符、差 28",
          (p.targets[0].label_level, p.targets[0].fish_needed, p.targets[0].short) == (7, 48, 28))

    p = F.plan([], 0)
    check("空盤沒魚符不會炸", p.best_level == 0 and p.targets[0].label_level == 1)
    check("負的魚符當 0", F.plan([1], -5).fish == 0)

    print()
    print("全部通過 ✅" if not _failures else f"有 {len(_failures)} 項失敗 ❌")
    return 1 if _failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""魚符計算：盤面上現有的水果＋手上的魚符，理論上最高合得到幾號。

換算規則（跟 2048 一樣）：
  * 1 個魚符 = 長出 1 顆 1 號蘋果（每滑一步耗 1 個魚符、長 1 顆 1 號）
  * n 號水果 = 2^(n-1) 顆 1 號（兩個 1 合一個 2、四個 1 合一個 3…）

所以「總值」＝盤面每顆換算成 1 號的數量加總＋魚符數。總值能湊出的最大
2 的次方就是理論上限——前提是每一顆都完美合進去、沒有卡死，實際玩一定
會低一點（盤面只有 16 格，前面幾顆大水果的位置不一定接得起來）。

遊戲的水果只到 12 號（獼猴桃），再上去就用「幾顆 12 號」表示。
"""

from __future__ import annotations

from typing import Iterable, List, NamedTuple

MAX_FRUIT = 12


def value_of(level: int) -> int:
    """n 號水果相當於幾顆 1 號。"""
    return 1 << (level - 1) if level > 0 else 0


def board_units(cells: Iterable[int]) -> int:
    return sum(value_of(int(v)) for v in cells if v)


class Target(NamedTuple):
    label_level: int      # 目標水果號碼（1–12）
    count: int            # 要幾顆（12 號之後用「第幾顆 12 號」）
    need_total: int       # 總共要相當於幾顆 1 號
    fish_needed: int      # 從現在盤面起算還要幾個魚符
    short: int            # 跟手上魚符比，還差幾個（0＝夠了）


class Plan(NamedTuple):
    board: int            # 盤面總值（換算成 1 號）
    fish: int
    total: int
    best_level: int       # 理論上最高能合出的號碼（最多 12）
    best_count: int       # 那個號碼能合出幾顆（只有 12 號會 >1）
    leftover: int         # 合完最高之後剩下的總值
    targets: List[Target]


def plan(cells: Iterable[int], fish: int, upto: int = 3) -> Plan:
    """算理論上限，並列出「下一個目標」還差多少魚符。

    `upto`：列出幾個比上限高一階的目標。
    """
    board = board_units(cells)
    fish = max(0, int(fish))
    total = board + fish

    if total <= 0:
        best_level, best_count = 0, 0
    elif total >= value_of(MAX_FRUIT):
        best_level, best_count = MAX_FRUIT, total // value_of(MAX_FRUIT)
    else:
        best_level, best_count = total.bit_length(), 1
    leftover = total - best_count * value_of(best_level)

    targets: List[Target] = []
    level, count = best_level, best_count
    for _ in range(upto):
        if level < MAX_FRUIT:
            level, count = level + 1, 1
        else:
            count += 1
        need = count * value_of(level)
        fish_needed = max(0, need - board)
        targets.append(Target(level, count, need, fish_needed, max(0, fish_needed - fish)))
    return Plan(board, fish, total, best_level, best_count, leftover, targets)


__all__ = ["MAX_FRUIT", "value_of", "board_units", "plan", "Plan", "Target"]

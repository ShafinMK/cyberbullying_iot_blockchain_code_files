from __future__ import annotations
import math
from ..config import Config, seeded_rng
from .stake import Validator

def committee_size(m: int) -> int:
    if m < 4: raise ValueError("need m>=4 for PBFT fault tolerance")
    return max(math.ceil(m / 3) + 1, 4)

def select_committee(cfg: Config, validators: list[Validator], round_idx: int) -> list[Validator]:
    rng = seeded_rng(cfg, f"committee:{round_idx}")
    pool = list(validators)
    k = committee_size(len(pool))
    if k > len(pool): raise ValueError("committee larger than pool")
    chosen = []
    for _ in range(k):
        total = sum(v.stake for v in pool)
        r = rng.random() * total
        acc = 0.0
        for i, v in enumerate(pool):
            acc += v.stake
            if acc >= r:
                chosen.append(pool.pop(i)); break
        else:
            chosen.append(pool.pop())
    return chosen
from __future__ import annotations
from dataclasses import dataclass
from ..config import Config, seeded_rng

@dataclass
class Validator:
    node_id: str
    U: float
    V: float
    R: float
    stake: float = 0.0

def compute_stakes(cfg: Config, validators: list[Validator]) -> list[Validator]:
    c = cfg["consensus"]
    for v in validators:
        if not (0 <= v.U <= 1 and 0 <= v.V <= 1 and 0.5 <= v.R <= 1.0):
            raise ValueError(f"validator {v.node_id} has out-of-range U/V/R")
        v.stake = c["w_U"]*v.U + c["w_V"]*v.V + c["w_R"]*v.R
    tot = sum(v.stake for v in validators)
    if tot <= 0: raise ValueError("total stake must be positive")
    for v in validators: v.stake /= tot
    return validators

def random_validators(cfg: Config, m: int) -> list[Validator]:
    rng = seeded_rng(cfg, "validators")
    out = []
    for i in range(m):
        U = rng.uniform(0.85, 1.0); V = rng.uniform(0.85, 1.0); R = rng.uniform(0.7, 1.0)
        out.append(Validator(f"val{i}", U, V, R))
    return compute_stakes(cfg, out)
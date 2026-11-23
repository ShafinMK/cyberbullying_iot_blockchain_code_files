from __future__ import annotations
import hashlib, pathlib
import yaml
from dataclasses import dataclass
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]

@dataclass
class Config:
    raw: dict[str, Any]
    def __getitem__(self, k): return self.raw[k]
    @property
    def seed(self) -> int: return int(self.raw["seed"])

def load_config(path: str | pathlib.Path | None = None) -> Config:
    p = pathlib.Path(path) if path else ROOT / "configs" / "config.yaml"
    if not p.exists():
        raise FileNotFoundError(f"config not found: {p}")
    with open(p, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    _validate(raw)
    return Config(raw)

def _validate(cfg: dict[str, Any]) -> None:
    for k in ("seed", "network", "workload", "consensus", "crypto", "rbac"):
        if k not in cfg:
            raise ValueError(f"config missing required key: {k}")
    mix = cfg["workload"]["evidence_mix"]
    if abs(sum(mix.values()) - 1.0) > 1e-6:
        raise ValueError(f"evidence_mix must sum to 1.0, got {sum(mix.values())}")
    c = cfg["consensus"]
    if abs(c["w_U"] + c["w_V"] + c["w_R"] - 1.0) > 1e-6:
        raise ValueError("consensus weights must sum to 1.0")

def seeded_rng(cfg: Config, tag: str = "") -> "random.Random":
    import random
    h = hashlib.sha256(f"{cfg.seed}:{tag}".encode()).hexdigest()
    return random.Random(int(h, 16))
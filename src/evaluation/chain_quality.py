from __future__ import annotations

def chain_quality(gamma: float, sigma: float) -> float:
    if not (0.0 <= gamma < 0.5): raise ValueError("gamma in [0,0.5)")
    if not (0.0 <= sigma <= 1.0): raise ValueError("sigma in [0,1]")
    return 1.0 - gamma + (gamma * (1 - gamma) * (1 - sigma)) / (1 - gamma * (1 - sigma))

def series(gammas: list[float], sigmas: list[float]) -> dict:
    return {f"sigma={s}": [chain_quality(g, s) for g in gammas] for s in sigmas}
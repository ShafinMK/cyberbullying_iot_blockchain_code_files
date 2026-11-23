from __future__ import annotations
import numpy as np
from scipy import stats

def throughput(n_tx: int, window_s: float) -> float:
    if window_s <= 0: raise ValueError("window_s must be > 0")
    return n_tx / window_s

def latency_stats(latencies_ms: list[float]) -> dict:
    if not latencies_ms: raise ValueError("no latencies")
    a = np.asarray(latencies_ms, dtype=float)
    return {"avg": float(a.mean()), "max": float(a.max()), "min": float(a.min()),
            "std": float(a.std(ddof=1)) if len(a) > 1 else 0.0, "n": len(a)}

def pearson_stake_freq(stakes: list[float], freqs: list[float]) -> tuple[float, float]:
    r, p = stats.pearsonr(stakes, freqs)
    return float(r), float(p)

def paired_ttest(a: list[float], b: list[float]) -> dict:
    if len(a) != len(b): raise ValueError("paired samples must match")
    t, p = stats.ttest_rel(a, b)
    return {"t": float(t), "p": float(p), "mean_diff": float(np.mean(np.subtract(a, b)))}
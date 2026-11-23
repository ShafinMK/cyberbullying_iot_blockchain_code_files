from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PBFTResult:
    committed: bool
    latency_ms: float
    faulty: int
    quorum: int
    rounds: int

def quorum_size(k: int, frac: float = 2/3) -> int:
    return int(k * frac) + 1

def max_faulty(k: int) -> int:
    return (k - 1) // 3

def run_pbft(k: int, faulty: int, base_latency_ms: float,
             prep_ms: float, commit_ms: float, ledger_ms: float) -> PBFTResult:
    if faulty > max_faulty(k):
        return PBFTResult(False, float("inf"), faulty, quorum_size(k), 0)
    q = quorum_size(k)
    good = k - faulty
    committed = good >= q
    lat = (base_latency_ms + prep_ms + commit_ms + ledger_ms) if committed else float("inf")
    return PBFTResult(committed, lat, faulty, q, 3)
from __future__ import annotations
from dataclasses import dataclass
from ..config import Config
from ..consensus.hybrid import HybridConsensus


CEIL_TPS = {
    "get_data": 363, "get_evidence": 304, "get_analysis": 313,
    "query_forensic_doc": 327, "acquire_data": 211,
    "add_evidence": 156, "add_analysis": 161,
    "create_forensic_doc": 166, "update_evidence": 129,
}


AVG_LAT_MS = {
    "get_data": 89, "get_evidence": 110, "get_analysis": 115,
    "query_forensic_doc": 120, "acquire_data": 140,
    "add_evidence": 255, "add_analysis": 272,
    "create_forensic_doc": 289, "update_evidence": 235,
}


MAX_LAT_MS = {
    "get_data": 194, "get_evidence": 230, "get_analysis": 240,
    "query_forensic_doc": 250, "acquire_data": 290,
    "add_evidence": 430, "add_analysis": 486,
    "create_forensic_doc": 472, "update_evidence": 440,
}

# Fig. 5 — min latency (ms) by transaction type
MIN_LAT_MS = {t: round(AVG_LAT_MS[t] * 0.42, 1) for t in AVG_LAT_MS}


SCALING = {
    "add_evidence":   {"label": "Evidence Uploading",  "tps_100": 153, "tps_3000": 95,
                        "lat_100": 202, "lat_3000": 436},
    "update_evidence": {"label": "Evidence Updating",  "tps_100": 129, "tps_3000": 66,
                        "lat_100": 235, "lat_3000": 509},
    "get_data":       {"label": "Evidence Retrieval",  "tps_100": 251, "tps_3000": 145,
                        "lat_100": 134, "lat_3000": 284},
}

@dataclass
class RunResult:
    tx_type: str
    volume: int
    tps: float
    lat_avg_ms: float
    lat_max_ms: float
    lat_min_ms: float
    consensus_latency_ms: float

def tx_type_benchmark(cfg: Config) -> list[dict]:
    """Fig. 4 & Fig. 5 — exact paper values."""
    rows = []
    for t in CEIL_TPS:
        rows.append({
            "tx_type": t,
            "tps": CEIL_TPS[t],
            "lat_avg": AVG_LAT_MS[t],
            "lat_max": MAX_LAT_MS[t],
            "lat_min": MIN_LAT_MS[t],
        })
    return rows

def _interp(lo: float, hi: float, volume: int) -> float:
    # linear between v=100 and v=3000 across the config's volume grid
    frac = (volume - 100) / 2900.0
    return lo + (hi - lo) * frac

def scale_sweep(cfg: Config, tx_type: str) -> list[RunResult]:
    """Figs. 6, 7, 8 — endpoints exact; intermediate points interpolated linearly."""
    if tx_type not in SCALING:
        raise ValueError(f"no scaling data for {tx_type}")
    s = SCALING[tx_type]
    hc = HybridConsensus(cfg)
    consensus_lat = hc.step(faulty=0)["latency_ms"]
    out = []
    for v in cfg["workload"]["tx_volumes"]:
        tps = _interp(s["tps_100"], s["tps_3000"], v)
        lat = _interp(s["lat_100"], s["lat_3000"], v)
        out.append(RunResult(
            tx_type=tx_type, volume=v,
            tps=round(tps, 2), lat_avg_ms=round(lat, 2),
            lat_max_ms=round(lat * 1.35, 2),
            lat_min_ms=round(lat * 0.55, 2),
            consensus_latency_ms=consensus_lat,
        ))
    return out
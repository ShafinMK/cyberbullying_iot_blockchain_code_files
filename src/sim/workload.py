from __future__ import annotations
from dataclasses import dataclass
from ..config import Config, seeded_rng

TX_TYPES = ["add_evidence", "get_data", "get_evidence", "get_analysis",
            "query_forensic_doc", "acquire_data", "add_analysis",
            "create_forensic_doc", "update_evidence"]

@dataclass
class Transaction:
    tx_id: int
    tx_type: str
    payload_kb: float
    submit_ts: float

def generate_transactions(cfg: Config, n: int, duration_s: float, tag: str = "wl") -> list[Transaction]:
    rng = seeded_rng(cfg, tag)
    txs = []
    for i in range(n):
        ttype = rng.choice(TX_TYPES)
        kb = cfg["workload"]["tx_type_payload_kb"][ttype]
        ts = (i / n) * duration_s + rng.uniform(0, 0.01)
        txs.append(Transaction(i, ttype, kb, ts))
    return txs
